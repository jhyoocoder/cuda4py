"""
Copyright (c) 2014, Samsung Electronics Co.,Ltd.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of Samsung Electronics Co.,Ltd..
"""

"""
cuda4py - CUDA cffi bindings and helper classes.
URL: https://github.com/ajkxyz/cuda4py
Original author: Alexey Kazantsev <a.kazantsev@samsung.com>
"""

"""
Tests some of the api in cuda4py.cudnn._cudnn module.
"""
import cuda4py as cu
import cuda4py.cudnn as cudnn
import gc
import logging
import numpy
import os
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.old_env = os.environ.get("CUDA_DEVICE")
        if self.old_env is None:
            os.environ["CUDA_DEVICE"] = "0"
        self.ctx = cu.Devices().create_some_context()
        self.cudnn = cudnn.CUDNN(self.ctx)
        self.path = os.path.dirname(__file__)
        if not len(self.path):
            self.path = "."

    def tearDown(self):
        if self.old_env is None:
            del os.environ["CUDA_DEVICE"]
        else:
            os.environ["CUDA_DEVICE"] = self.old_env
        del self.old_env
        del self.cudnn
        del self.ctx
        gc.collect()

    def test_constants(self):
        self.assertEqual(cudnn.CUDNN_STATUS_SUCCESS, 0)
        self.assertEqual(cudnn.CUDNN_STATUS_NOT_INITIALIZED, 1)
        self.assertEqual(cudnn.CUDNN_STATUS_ALLOC_FAILED, 2)
        self.assertEqual(cudnn.CUDNN_STATUS_BAD_PARAM, 3)
        self.assertEqual(cudnn.CUDNN_STATUS_INTERNAL_ERROR, 4)
        self.assertEqual(cudnn.CUDNN_STATUS_INVALID_VALUE, 5)
        self.assertEqual(cudnn.CUDNN_STATUS_ARCH_MISMATCH, 6)
        self.assertEqual(cudnn.CUDNN_STATUS_MAPPING_ERROR, 7)
        self.assertEqual(cudnn.CUDNN_STATUS_EXECUTION_FAILED, 8)
        self.assertEqual(cudnn.CUDNN_STATUS_NOT_SUPPORTED, 9)
        self.assertEqual(cudnn.CUDNN_STATUS_LICENSE_ERROR, 10)

        self.assertEqual(cudnn.CUDNN_DATA_FLOAT, 0)
        self.assertEqual(cudnn.CUDNN_DATA_DOUBLE, 1)

        self.assertEqual(cudnn.CUDNN_TENSOR_NCHW, 0)
        self.assertEqual(cudnn.CUDNN_TENSOR_NHWC, 1)

        self.assertEqual(cudnn.CUDNN_CONVOLUTION, 0)
        self.assertEqual(cudnn.CUDNN_CROSS_CORRELATION, 1)

        self.assertEqual(cudnn.CUDNN_CONVOLUTION_FWD_NO_WORKSPACE, 0)
        self.assertEqual(cudnn.CUDNN_CONVOLUTION_FWD_PREFER_FASTEST, 1)
        self.assertEqual(
            cudnn.CUDNN_CONVOLUTION_FWD_SPECIFY_WORKSPACE_LIMIT, 2)

        self.assertEqual(cudnn.CUDNN_CONVOLUTION_FWD_ALGO_IMPLICIT_GEMM, 0)
        self.assertEqual(
            cudnn.CUDNN_CONVOLUTION_FWD_ALGO_IMPLICIT_PRECOMP_GEMM, 1)
        self.assertEqual(cudnn.CUDNN_CONVOLUTION_FWD_ALGO_GEMM, 2)
        self.assertEqual(cudnn.CUDNN_CONVOLUTION_FWD_ALGO_DIRECT, 3)

    def test_errors(self):
        idx = cu.CU.ERRORS[cudnn.CUDNN_STATUS_NOT_INITIALIZED].find(" | ")
        self.assertGreater(idx, 0)

    def test_tensor_descriptor(self):
        d = cudnn.TensorDescriptor()
        self.assertIsNotNone(d.handle)
        for dt in (cudnn.CUDNN_DATA_DOUBLE, cudnn.CUDNN_DATA_FLOAT):
            for fmt in (cudnn.CUDNN_TENSOR_NCHW, cudnn.CUDNN_TENSOR_NHWC):
                d.set_4d(fmt, dt, 100, 50, 217, 215)
        del d

    def test_filter_descriptor(self):
        d = cudnn.FilterDescriptor()
        self.assertIsNotNone(d.handle)
        for dt in (cudnn.CUDNN_DATA_DOUBLE, cudnn.CUDNN_DATA_FLOAT):
            d.set_4d(dt, 64, 3, 11, 12)
        del d

    def test_convolution_descriptor(self):
        d = cudnn.ConvolutionDescriptor()
        self.assertIsNotNone(d.handle)
        for mode in (cudnn.CUDNN_CROSS_CORRELATION, cudnn.CUDNN_CONVOLUTION):
            d.set_2d(1, 2, 3, 4, 1, 1, mode)
        del d

    def _init_descriptors(self, include_out=False):
        conv = cudnn.ConvolutionDescriptor()
        conv.set_2d(5, 4, 2, 1)
        inp = cudnn.TensorDescriptor()
        inp.set_4d(cudnn.CUDNN_TENSOR_NCHW, cudnn.CUDNN_DATA_FLOAT,
                   100, 8, 208, 224)
        filter = cudnn.FilterDescriptor()
        filter.set_4d(cudnn.CUDNN_DATA_FLOAT, 64, 8, 11, 7)
        if not include_out:
            return conv, inp, filter
        n, c, h, w = cudnn.CUDNN.get_convolution_2d_forward_output_dim(
            conv, inp, filter)
        out = cudnn.TensorDescriptor()
        out.set_4d(cudnn.CUDNN_TENSOR_NCHW, cudnn.CUDNN_DATA_FLOAT, n, c, h, w)
        return conv, inp, filter, out

    def test_get_convolution_2d_forward_output_dim(self):
        conv, inp, filter = self._init_descriptors()
        n, c, h, w = cudnn.CUDNN.get_convolution_2d_forward_output_dim(
            conv, inp, filter)
        self.assertEqual(n, 100)
        self.assertEqual(c, 64)
        self.assertEqual(h, 104)
        self.assertEqual(w, 226)

    def test_get_convolutional_forward_algorithm(self):
        logging.debug("ENTER: test_get_convolutional_forward_algorithm")
        conv, inp, filter, out = self._init_descriptors(True)
        algo = self.cudnn.get_convolution_forward_algorithm(
            inp, filter, conv, out)
        self.assertGreaterEqual(algo, 0)
        logging.debug("Fastest algo: %d", algo)
        algo = self.cudnn.get_convolution_forward_algorithm(
            inp, filter, conv, out,
            cudnn.CUDNN_CONVOLUTION_FWD_SPECIFY_WORKSPACE_LIMIT,
            2 * 1024 * 1024 * 1024)
        logging.debug("With 2Gb limit algo: %d", algo)
        logging.debug("EXIT: test_get_convolutional_forward_algorithm")

    def test_get_convolution_forward_workspace_size(self):
        logging.debug("ENTER: test_get_convolution_forward_workspace_size")
        conv, inp, filter, out = self._init_descriptors(True)
        algo = self.cudnn.get_convolution_forward_algorithm(
            inp, filter, conv, out)
        for a in (algo, cudnn.CUDNN_CONVOLUTION_FWD_ALGO_IMPLICIT_GEMM,
                  cudnn.CUDNN_CONVOLUTION_FWD_ALGO_IMPLICIT_PRECOMP_GEMM,
                  cudnn.CUDNN_CONVOLUTION_FWD_ALGO_GEMM,
                  cudnn.CUDNN_CONVOLUTION_FWD_ALGO_DIRECT):
            try:
                sz = self.cudnn.get_convolution_forward_workspace_size(
                    inp, filter, conv, out, a)
            except cu.CUDARuntimeError as e:
                self.assertEqual(e.code, cudnn.CUDNN_STATUS_NOT_SUPPORTED)
                continue
            self.assertGreaterEqual(sz, 0)
            logging.debug("algo=%d size=%d", a, sz)
        logging.debug("EXIT: test_get_convolution_forward_workspace_size")

    def test_convolution_forward(self):
        logging.debug("ENTER: test_convolution_forward")

        conv_desc = cudnn.ConvolutionDescriptor()
        conv_desc.set_2d(5, 4, 2, 1)

        inp_data = numpy.zeros((100, 8, 104, 112), dtype=numpy.float32)
        inp_data[:] = 0.1
        inp_desc = cudnn.TensorDescriptor()
        inp_desc.set_4d(cudnn.CUDNN_TENSOR_NCHW, cudnn.CUDNN_DATA_FLOAT,
                        *inp_data.shape)
        inp_buf = cu.MemAlloc(self.ctx, inp_data)

        filter_data = numpy.zeros((64, 8, 11, 7), dtype=numpy.float32)
        filter_data[:] = 0.3
        filter_desc = cudnn.FilterDescriptor()
        filter_desc.set_4d(cudnn.CUDNN_DATA_FLOAT, *filter_data.shape)
        filter_buf = cu.MemAlloc(self.ctx, filter_data)

        n, c, h, w = cudnn.CUDNN.get_convolution_2d_forward_output_dim(
            conv_desc, inp_desc, filter_desc)
        out_data = numpy.zeros((n, c, h, w), dtype=numpy.float32)
        out_desc = cudnn.TensorDescriptor()
        out_desc.set_4d(cudnn.CUDNN_TENSOR_NCHW, cudnn.CUDNN_DATA_FLOAT,
                        *out_data.shape)
        out_buf = cu.MemAlloc(self.ctx, out_data)

        workspace = cu.MemAlloc(self.ctx, 512 * 1024 * 1024)
        algo = self.cudnn.get_convolution_forward_algorithm(
            inp_desc, filter_desc, conv_desc, out_desc,
            cudnn.CUDNN_CONVOLUTION_FWD_SPECIFY_WORKSPACE_LIMIT,
            workspace.size)

        alpha = numpy.ones(1, dtype=numpy.float32)
        beta = numpy.zeros(1, dtype=numpy.float32)
        self.cudnn.convolution_forward(
            alpha, inp_desc, inp_buf, filter_desc, filter_buf, conv_desc,
            algo, workspace, workspace.size, beta, out_desc, out_buf)

        out_buf.to_host(out_data)
        self.assertEqual(numpy.count_nonzero(out_data), out_data.size)

        logging.debug("EXIT: test_convolution_forward")

    def test_convolution_backward_bias(self):
        logging.debug("ENTER: test_convolution_backward_bias")

        bperr_data = numpy.zeros((100, 64, 104, 226), dtype=numpy.float32)
        bperr_data[:] = 0.1
        bperr_desc = cudnn.TensorDescriptor()
        bperr_desc.set_4d(cudnn.CUDNN_TENSOR_NCHW, cudnn.CUDNN_DATA_FLOAT,
                          *bperr_data.shape)
        bperr_buf = cu.MemAlloc(self.ctx, bperr_data)

        gd_data = numpy.zeros(64, dtype=numpy.float32)
        gd_desc = cudnn.TensorDescriptor()
        gd_desc.set_4d(cudnn.CUDNN_TENSOR_NCHW, cudnn.CUDNN_DATA_FLOAT,
                       1, gd_data.size, 1, 1)
        gd_buf = cu.MemAlloc(self.ctx, gd_data)

        alpha = numpy.ones(1, dtype=numpy.float32)
        beta = numpy.zeros(1, dtype=numpy.float32)
        self.cudnn.convolution_backward_bias(alpha, bperr_desc, bperr_buf,
                                             beta, gd_desc, gd_buf)

        gd_buf.to_host(gd_data)
        self.assertEqual(numpy.count_nonzero(gd_data), gd_data.size)

        logging.debug("EXIT: test_convolution_backward_bias")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()