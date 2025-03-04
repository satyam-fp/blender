/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup freestyle
 */

#pragma once

#include "../BPy_StrokeShader.h"

///////////////////////////////////////////////////////////////////////////////////////////

extern PyTypeObject SamplingShader_Type;

#define BPy_SamplingShader_Check(v) \
  (PyObject_IsInstance((PyObject *)v, (PyObject *)&SamplingShader_Type))

/*---------------------------Python BPy_SamplingShader structure definition----------*/
typedef struct {
  BPy_StrokeShader py_ss;
} BPy_SamplingShader;

///////////////////////////////////////////////////////////////////////////////////////////
