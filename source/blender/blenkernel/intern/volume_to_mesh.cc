/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

#include <fmt/format.h>
#include <vector>

#include "BLI_math_vector_types.hh"
#include "BLI_span.hh"

#include "BKE_mesh.hh"
#include "BKE_volume_grid.hh"
#include "BKE_volume_openvdb.hh"

#ifdef WITH_OPENVDB
#  include <openvdb/tools/GridTransformer.h>
#  include <openvdb/tools/VolumeToMesh.h>
#endif

#include "BKE_volume_to_mesh.hh"

#include "BLT_translation.hh"

namespace blender::bke {

#ifdef WITH_OPENVDB

struct VolumeToMeshOp {
  const openvdb::GridBase &base_grid;
  const VolumeToMeshResolution resolution;
  const float threshold;
  const float adaptivity;
  std::vector<openvdb::Vec3s> verts;
  std::vector<openvdb::Vec3I> tris;
  std::vector<openvdb::Vec4I> quads;
  std::string error;

  template<typename GridType> bool operator()()
  {
    if constexpr (std::is_scalar_v<typename GridType::ValueType>) {
      this->generate_mesh_data<GridType>();
      return true;
    }
    return false;
  }

  template<typename GridType> void generate_mesh_data()
  {
    const GridType &grid = static_cast<const GridType &>(base_grid);

    if (this->resolution.mode == VOLUME_TO_MESH_RESOLUTION_MODE_GRID) {
      this->grid_to_mesh(grid);
      return;
    }

    const float resolution_factor = this->compute_resolution_factor(base_grid);
    typename GridType::Ptr temp_grid = this->create_grid_with_changed_resolution(
        grid, resolution_factor);
    this->grid_to_mesh(*temp_grid);
  }

  template<typename GridType>
  typename GridType::Ptr create_grid_with_changed_resolution(const GridType &old_grid,
                                                             const float resolution_factor)
  {
    BLI_assert(resolution_factor > 0.0f);

    openvdb::Mat4R xform;
    xform.setToScale(openvdb::Vec3d(resolution_factor));
    openvdb::tools::GridTransformer transformer{xform};

    typename GridType::Ptr new_grid = GridType::create();
    transformer.transformGrid<openvdb::tools::BoxSampler>(old_grid, *new_grid);
    new_grid->transform() = old_grid.transform();
    new_grid->transform().preScale(1.0f / resolution_factor);
    return new_grid;
  }

  float compute_resolution_factor(const openvdb::GridBase &grid) const
  {
    const openvdb::Vec3s voxel_size{grid.voxelSize()};
    const float current_voxel_size = std::max({voxel_size[0], voxel_size[1], voxel_size[2]});
    const float desired_voxel_size = this->compute_desired_voxel_size(grid);
    return current_voxel_size / desired_voxel_size;
  }

  float compute_desired_voxel_size(const openvdb::GridBase &grid) const
  {
    if (this->resolution.mode == VOLUME_TO_MESH_RESOLUTION_MODE_VOXEL_SIZE) {
      return this->resolution.settings.voxel_size;
    }
    const openvdb::CoordBBox coord_bbox = base_grid.evalActiveVoxelBoundingBox();
    const openvdb::BBoxd bbox = grid.transform().indexToWorld(coord_bbox);
    const float max_extent = bbox.extents()[bbox.maxExtent()];
    const float voxel_size = max_extent / this->resolution.settings.voxel_amount;
    return voxel_size;
  }

  template<typename GridType> void grid_to_mesh(const GridType &grid)
  {
    try {
      openvdb::tools::volumeToMesh(
          grid, this->verts, this->tris, this->quads, this->threshold, this->adaptivity);
    }
    catch (const std::exception &e) {
      this->error = fmt::format(fmt::runtime(TIP_("OpenVDB error: {}")), e.what());
      this->verts.clear();
      this->tris.clear();
      this->quads.clear();
    }

    /* Better align generated mesh with volume (see #85312). */
    openvdb::Vec3s offset = grid.voxelSize() / 2.0f;
    for (openvdb::Vec3s &position : this->verts) {
      position += offset;
    }
  }
};

void fill_mesh_from_openvdb_data(const Span<openvdb::Vec3s> vdb_verts,
                                 const Span<openvdb::Vec3I> vdb_tris,
                                 const Span<openvdb::Vec4I> vdb_quads,
                                 const int vert_offset,
                                 const int face_offset,
                                 const int loop_offset,
                                 MutableSpan<float3> vert_positions,
                                 MutableSpan<int> face_offsets,
                                 MutableSpan<int> corner_verts)
{
  /* Write vertices. */
  vert_positions.slice(vert_offset, vdb_verts.size()).copy_from(vdb_verts.cast<float3>());

  /* Write triangles. */
  for (const int i : vdb_tris.index_range()) {
    face_offsets[face_offset + i] = loop_offset + 3 * i;
    for (int j = 0; j < 3; j++) {
      /* Reverse vertex order to get correct normals. */
      corner_verts[loop_offset + 3 * i + j] = vert_offset + vdb_tris[i][2 - j];
    }
  }

  /* Write quads. */
  const int quad_offset = face_offset + vdb_tris.size();
  const int quad_loop_offset = loop_offset + vdb_tris.size() * 3;
  for (const int i : vdb_quads.index_range()) {
    face_offsets[quad_offset + i] = quad_loop_offset + 4 * i;
    for (int j = 0; j < 4; j++) {
      /* Reverse vertex order to get correct normals. */
      corner_verts[quad_loop_offset + 4 * i + j] = vert_offset + vdb_quads[i][3 - j];
    }
  }
}

bke::VolumeToMeshDataResult volume_to_mesh_data(const openvdb::GridBase &grid,
                                                const VolumeToMeshResolution &resolution,
                                                const float threshold,
                                                const float adaptivity)
{
  const VolumeGridType grid_type = bke::volume_grid::get_type(grid);

  VolumeToMeshOp to_mesh_op{grid, resolution, threshold, adaptivity};
  if (!BKE_volume_grid_type_operation(grid_type, to_mesh_op)) {
    return {};
  }
  return {{std::move(to_mesh_op.verts), std::move(to_mesh_op.tris), std::move(to_mesh_op.quads)},
          to_mesh_op.error};
}

Mesh *volume_to_mesh(const openvdb::GridBase &grid,
                     const VolumeToMeshResolution &resolution,
                     const float threshold,
                     const float adaptivity)
{
  using namespace blender::bke;
  const OpenVDBMeshData mesh_data =
      volume_to_mesh_data(grid, resolution, threshold, adaptivity).data;

  const int tot_loops = 3 * mesh_data.tris.size() + 4 * mesh_data.quads.size();
  const int tot_faces = mesh_data.tris.size() + mesh_data.quads.size();
  Mesh *mesh = BKE_mesh_new_nomain(mesh_data.verts.size(), 0, tot_faces, tot_loops);

  fill_mesh_from_openvdb_data(mesh_data.verts,
                              mesh_data.tris,
                              mesh_data.quads,
                              0,
                              0,
                              0,
                              mesh->vert_positions_for_write(),
                              mesh->face_offsets_for_write(),
                              mesh->corner_verts_for_write());

  mesh_calc_edges(*mesh, false, false);
  mesh_smooth_set(*mesh, false);

  mesh->tag_overlapping_none();

  return mesh;
}

Mesh *volume_grid_to_mesh(const openvdb::GridBase &grid,
                          const float threshold,
                          const float adaptivity)
{
  return volume_to_mesh(grid, {VOLUME_TO_MESH_RESOLUTION_MODE_GRID}, threshold, adaptivity);
}

#endif /* WITH_OPENVDB */

}  // namespace blender::bke
