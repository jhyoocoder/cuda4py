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
cuDNN helper classes.
"""
import cuda4py._impl.cudnn._cffi as cudnnffi
from cuda4py._impl.cudnn._cffi import (
    CUDNN_TENSOR_NCHW, CUDNN_CROSS_CORRELATION, CUDNN_POOLING_MAX,
    CUDNN_NOT_PROPAGATE_NAN, CUDNN_LINEAR_INPUT, CUDNN_UNIDIRECTIONAL,
    CUDNN_LSTM, CUDNN_DATA_FLOAT, CUDNN_CONVOLUTION_FWD_PREFER_FASTEST,
    CUDNN_CONVOLUTION_BWD_FILTER_PREFER_FASTEST,
    CUDNN_CONVOLUTION_BWD_FILTER_SPECIFY_WORKSPACE_LIMIT,
    CUDNN_CONVOLUTION_BWD_FILTER_NO_WORKSPACE,
    CUDNN_CONVOLUTION_BWD_DATA_PREFER_FASTEST,
    CUDNN_CONVOLUTION_BWD_DATA_SPECIFY_WORKSPACE_LIMIT,
    CUDNN_CONVOLUTION_BWD_DATA_NO_WORKSPACE)
from cuda4py._py import CU


class Descriptor(object):
    """CUDNN descriptor base class.
    """
    def __init__(self):
        self._lib = cudnnffi.lib
        self._handle = None
        self._create()

    def _create(self):
        """Calls cudnnCreate*Descriptor and assigns self._handle
        """
        raise NotImplementedError()

    def _destroy(self):
        """Calls cudnnDestroy*Descriptor on self._handle
        """
        raise NotImplementedError()

    def __int__(self):
        return self.handle

    @property
    def handle(self):
        return self._handle

    def _release(self):
        if self._lib is not None and self.handle is not None:
            self._destroy()
            self._handle = None

    def __del__(self):
        self._release()


class TensorDescriptor(Descriptor):
    """CUDNN tensor descriptor.
    """
    def _create(self):
        handle = cudnnffi.ffi.new("cudnnTensorDescriptor_t *")
        err = self._lib.cudnnCreateTensorDescriptor(handle)
        if err:
            raise CU.error("cudnnCreateTensorDescriptor", err)
        self._handle = int(handle[0])

    def _destroy(self):
        self._lib.cudnnDestroyTensorDescriptor(self.handle)

    def set_4d(self, fmt, data_type, n, c, h, w):
        """Initializes tensor descriptor into a 4D tensor.

        Parameters:
            fmt: CUDNN_TENSOR_NCHW or CUDNN_TENSOR_NHWC.
            data_type: CUDNN_DATA_FLOAT or CUDNN_DATA_DOUBLE.
            n: number of images.
            c: number of image channels.
            h: image height.
            w: image width.
        """
        err = self._lib.cudnnSetTensor4dDescriptor(
            self.handle, fmt, data_type, n, c, h, w)
        if err:
            raise CU.error("cudnnSetTensor4dDescriptor", err)


class FilterDescriptor(Descriptor):
    """CUDNN filter descriptor.
    """
    def _create(self):
        handle = cudnnffi.ffi.new("cudnnFilterDescriptor_t *")
        err = self._lib.cudnnCreateFilterDescriptor(handle)
        if err:
            raise CU.error("cudnnCreateFilterDescriptor", err)
        self._handle = int(handle[0])

    def _destroy(self):
        self._lib.cudnnDestroyFilterDescriptor(self.handle)

    def set_4d(self, data_type, k, c, h, w, fmt=CUDNN_TENSOR_NCHW):
        """Initializes tensor descriptor into a 4D tensor.

        Parameters:
            data_type: CUDNN_DATA_FLOAT or CUDNN_DATA_DOUBLE.
            k: number of kernels.
            c: number of image channels.
            h: image height.
            w: image width.
            fmt: tensor format for weights.
        """
        if cudnnffi.cudnn_version < 5000:
            err = self._lib.cudnnSetFilter4dDescriptor(
                self.handle, data_type, k, c, h, w)
        else:
            err = self._lib.cudnnSetFilter4dDescriptor(
                self.handle, data_type, fmt, k, c, h, w)
        if err:
            raise CU.error("cudnnSetFilter4dDescriptor", err)


class ConvolutionDescriptor(Descriptor):
    """CUDNN convolution descriptor.
    """
    def _create(self):
        handle = cudnnffi.ffi.new("cudnnConvolutionDescriptor_t *")
        err = self._lib.cudnnCreateConvolutionDescriptor(handle)
        if err:
            raise CU.error("cudnnCreateConvolutionDescriptor", err)
        self._handle = int(handle[0])

    def _destroy(self):
        self._lib.cudnnDestroyConvolutionDescriptor(self.handle)

    def set_2d(self, pad_h, pad_w, u, v, upscalex=1, upscaley=1,
               mode=CUDNN_CROSS_CORRELATION):
        """Initializes tensor descriptor into a 4D tensor.

        Parameters:
            pad_h: zero-padding height (top & bottom).
            pad_w: zero-padding width (left & right).
            u: vertical filter stride.
            v: horizontal filter stride.
            upscalex: upscale the input in x-direction.
            upscaley: upscale the input in y-direction.
            mode: CUDNN_CROSS_CORRELATION or CUDNN_CROSS_CONVOLUTION.
        """
        err = self._lib.cudnnSetConvolution2dDescriptor(
            self.handle, pad_h, pad_w, u, v, upscalex, upscaley, mode)
        if err:
            raise CU.error("cudnnSetConvolution2dDescriptor", err)


class PoolingDescriptor(Descriptor):
    """CUDNN pooling descriptor.
    """
    def _create(self):
        handle = cudnnffi.ffi.new("cudnnPoolingDescriptor_t *")
        err = self._lib.cudnnCreatePoolingDescriptor(handle)
        if err:
            raise CU.error("cudnnCreatePoolingDescriptor", err)
        self._handle = int(handle[0])

    def _destroy(self):
        self._lib.cudnnDestroyPoolingDescriptor(self.handle)

    def set_2d(self, window_hw, padding_vh, stride_vh, mode=CUDNN_POOLING_MAX,
               maxpooling_nan_opt=CUDNN_NOT_PROPAGATE_NAN):
        """Initializes tensor descriptor into a 4D tensor.

        Parameters:
            window_hw: tuple of ints for pooling window (height, width).
            padding_vh: tuple for padding (vertical, horizontal).
            stride_vh: tuple for stride (vertical, horizontal).
            mode: pooling mode.
        """
        if cudnnffi.cudnn_version < 5000:
            err = self._lib.cudnnSetPooling2dDescriptor(
                self.handle, mode, window_hw[0], window_hw[1],
                padding_vh[0], padding_vh[1], stride_vh[0], stride_vh[1])
        else:
            err = self._lib.cudnnSetPooling2dDescriptor(
                self.handle, mode, maxpooling_nan_opt,
                window_hw[0], window_hw[1],
                padding_vh[0], padding_vh[1], stride_vh[0], stride_vh[1])
        if err:
            raise CU.error("cudnnSetPooling2dDescriptor", err)


class DropoutDescriptor(Descriptor):
    """CUDNN dropout descriptor.
    """
    def _create(self):
        handle = cudnnffi.ffi.new("cudnnDropoutDescriptor_t *")
        err = self._lib.cudnnCreateDropoutDescriptor(handle)
        if err:
            raise CU.error("cudnnCreateDropoutDescriptor", err)
        self._handle = int(handle[0])

    def _destroy(self):
        self._lib.cudnnDestroyDropoutDescriptor(self.handle)


class RNNDescriptor(Descriptor):
    """CUDNN RNN descriptor.
    """
    def _create(self):
        handle = cudnnffi.ffi.new("cudnnRNNDescriptor_t *")
        err = self._lib.cudnnCreateRNNDescriptor(handle)
        if err:
            raise CU.error("cudnnCreateRNNDescriptor", err)
        self._handle = int(handle[0])

    def _destroy(self):
        self._lib.cudnnDestroyRNNDescriptor(self.handle)

    def set(self, hidden_size, seq_length, num_layers, dropout_desc,
            input_mode=CUDNN_LINEAR_INPUT, direction=CUDNN_UNIDIRECTIONAL,
            mode=CUDNN_LSTM, data_type=CUDNN_DATA_FLOAT):
        """Initializes RNN descriptor.

        Parameters:
            hidden_size: size of the internal hidden state for each layer.
            seq_length: number of iterations to unroll over.
            num_layers: number of layers.
            dropout_desc: DropoutDescriptor instance.
            input_mode: specifies the behavior at the input to the first layer.
            direction: specifies the recurrence pattern, e.g. bidirectional.
            mode: the type of RNN to compute.
            data_type: math precision.
        """
        err = self._lib.cudnnSetRNNDescriptor(
            self.handle, hidden_size, seq_length, num_layers, dropout_desc,
            input_mode, direction, mode, data_type)
        if err:
            raise CU.error("cudnnSetRNNDescriptor", err)


class CUDNN(object):
    """CUDNN functions can be invoked from this class.
    """
    def __init__(self, context):
        self._context = context
        self._lib = None
        context._add_ref(self)
        cudnnffi.initialize()
        handle = cudnnffi.ffi.new("cudnnHandle_t *")
        with context:
            err = cudnnffi.lib.cudnnCreate(handle)
        if err:
            self._handle = None
            raise CU.error("cudnnCreate", err)
        self._lib = cudnnffi.lib  # to hold the reference
        self._handle = int(handle[0])

    @property
    def version(self):
        return cudnnffi.cudnn_version

    def __int__(self):
        return self.handle

    @property
    def handle(self):
        return self._handle

    @property
    def context(self):
        return self._context

    @staticmethod
    def get_convolution_2d_forward_output_dim(conv_desc, input_desc,
                                              filter_desc):
        """Returns tuple of n, c, h, w for an output.
        """
        n, c, h, w = (cudnnffi.ffi.new("int *") for _ in range(4))
        err = cudnnffi.lib.cudnnGetConvolution2dForwardOutputDim(
            conv_desc, input_desc, filter_desc, n, c, h, w)
        if err:
            raise CU.error("cudnnGetConvolution2dForwardOutputDim", err)
        return int(n[0]), int(c[0]), int(h[0]), int(w[0])

    @staticmethod
    def get_pooling_2d_forward_output_dim(pooling_desc, input_desc):
        """Returns tuple of n, c, h, w for an output.
        """
        n, c, h, w = (cudnnffi.ffi.new("int *") for _ in range(4))
        err = cudnnffi.lib.cudnnGetPooling2dForwardOutputDim(
            pooling_desc, input_desc, n, c, h, w)
        if err:
            raise CU.error("cudnnGetPooling2dForwardOutputDim", err)
        return int(n[0]), int(c[0]), int(h[0]), int(w[0])

    def get_convolution_forward_algorithm(
            self, src_desc, filter_desc, conv_dec, dest_desc,
            preference=CUDNN_CONVOLUTION_FWD_PREFER_FASTEST, memory_limit=0):
        """Returns forward algorithm based on parameters.
        """
        algo = cudnnffi.ffi.new("cudnnConvolutionFwdAlgo_t *")
        err = self._lib.cudnnGetConvolutionForwardAlgorithm(
            self.handle, src_desc, filter_desc, conv_dec, dest_desc,
            preference, memory_limit, algo)
        if err:
            raise CU.error("cudnnGetConvolutionForwardAlgorithm", err)
        return int(algo[0])

    def get_convolution_forward_workspace_size(
            self, src_desc, filter_desc, conv_dec, dest_desc, algo):
        """Returns required size of the additional temporary buffer
        for the specified forward convolution algorithm.
        """
        size = cudnnffi.ffi.new("size_t *")
        err = self._lib.cudnnGetConvolutionForwardWorkspaceSize(
            self.handle, src_desc, filter_desc, conv_dec, dest_desc,
            algo, size)
        if err:
            raise CU.error("cudnnGetConvolutionForwardWorkspaceSize", err)
        return int(size[0])

    def convolution_forward(
            self, alpha, src_desc, src_data, filter_desc, filter_data,
            conv_desc, algo, workspace, workspace_size,
            beta, dest_desc, dest_data):
        """Does convolution forward propagation.

        Parameters:
            alpha: src_data multiplier (numpy array with one element).
            beta: dest_data multiplier (numpy array with one element).
        """
        size = cudnnffi.ffi.new("size_t *")
        err = self._lib.cudnnConvolutionForward(
            self.handle, CU.extract_ptr(alpha), src_desc, src_data,
            filter_desc, filter_data, conv_desc,
            algo, workspace, workspace_size,
            CU.extract_ptr(beta), dest_desc, dest_data)
        if err:
            raise CU.error("cudnnConvolutionForward", err)
        return int(size[0])

    def convolution_backward_bias(self, alpha, src_desc, src_data,
                                  beta, dest_desc, dest_data):
        """Computes gradient for the bias.

        Parameters:
            alpha: src_data multiplier (numpy array with one element).
            beta: dest_data multiplier (numpy array with one element).
            src_data: error for backpropagation.
            dest_data: gradient for the bias.
        """
        err = self._lib.cudnnConvolutionBackwardBias(
            self.handle, CU.extract_ptr(alpha), src_desc, src_data,
            CU.extract_ptr(beta), dest_desc, dest_data)
        if err:
            raise CU.error("cudnnConvolutionBackwardBias", err)

    def get_convolution_backward_filter_algorithm(
            self, src_desc, diff_desc, conv_dec, grad_desc,
            preference=CUDNN_CONVOLUTION_BWD_FILTER_PREFER_FASTEST,
            memory_limit=0):
        """Returns backward filter algorithm based on parameters.

        Parameters:
            src_desc: descriptor of input from the forward pass.
            diff_desc: descriptor of the error for backpropagation.
            conv_desc: descriptor of the convolution (padding, stride, etc.).
            grad_desc: descriptor of the gradient for convolutional kernels.
        """
        algo = cudnnffi.ffi.new("cudnnConvolutionBwdFilterAlgo_t *")
        err = self._lib.cudnnGetConvolutionBackwardFilterAlgorithm(
            self.handle, src_desc, diff_desc, conv_dec, grad_desc,
            preference, memory_limit, algo)
        if err:
            raise CU.error("cudnnGetConvolutionBackwardFilterAlgorithm", err)
        return int(algo[0])

    def get_convolution_backward_filter_workspace_size(
            self, src_desc, diff_desc, conv_desc, grad_desc, algo):
        """Returns required size of the additional temporary buffer
        for the specified backward filter convolution algorithm.

        Parameters:
            src_desc: descriptor of input from the forward pass.
            diff_desc: descriptor of the error for backpropagation.
            conv_desc: descriptor of the convolution (padding, stride, etc.).
            grad_desc: descriptor of the gradient for convolutional kernels.
            algo: algorithm for the computing of kernel's gradient.
        """
        size = cudnnffi.ffi.new("size_t *")
        err = self._lib.cudnnGetConvolutionBackwardFilterWorkspaceSize(
            self.handle, src_desc, diff_desc, conv_desc, grad_desc, algo, size)
        if err:
            raise CU.error("cudnnGetConvolutionBackwardFilterWorkspaceSize",
                           err)
        return int(size[0])

    def convolution_backward_filter(
            self, alpha, src_desc, src_data, diff_desc, diff_data, conv_desc,
            beta, grad_desc, grad_data,
            algo=None, workspace=None, workspace_size=0):
        """Computes gradient for the convolutional kernels.

        Parameters:
            alpha: src_data multiplier (numpy array with one element).
            beta: grad_data multiplier (numpy array with one element).
            src_data: input from the forward pass.
            diff_data: error for backpropagation.
            grad_data: gradient for convolutional kernels.
        """
        if self.version < 4000:
            err = self._lib.cudnnConvolutionBackwardFilter(
                self.handle, CU.extract_ptr(alpha), src_desc, src_data,
                diff_desc, diff_data, conv_desc,
                CU.extract_ptr(beta), grad_desc, grad_data)
            if err:
                raise CU.error("cudnnConvolutionBackwardFilter", err)
            return
        if algo is None:
            # Get the algorithm
            algo = self.get_convolution_backward_filter_algorithm(
                src_desc, diff_desc, conv_desc, grad_desc,
                CUDNN_CONVOLUTION_BWD_FILTER_SPECIFY_WORKSPACE_LIMIT
                if workspace_size else
                CUDNN_CONVOLUTION_BWD_FILTER_NO_WORKSPACE, workspace_size)
        # Compute weights gradient with the selected algorithm
        err = self._lib.cudnnConvolutionBackwardFilter(
            self.handle, CU.extract_ptr(alpha), src_desc, src_data,
            diff_desc, diff_data, conv_desc,
            algo, 0 if workspace is None else workspace, workspace_size,
            CU.extract_ptr(beta), grad_desc, grad_data)
        if err:
            raise CU.error("cudnnConvolutionBackwardFilter", err)

    def get_convolution_backward_data_algorithm(
            self, filter_desc, diff_desc, conv_desc, grad_desc,
            preference=CUDNN_CONVOLUTION_BWD_DATA_PREFER_FASTEST,
            memory_limit=0):
        """Returns backward data algorithm based on parameters.

        Parameters:
            filter_desc: descriptor of the convolutional kernels.
            diff_desc: descriptor of the error for backpropagation.
            conv_desc: descriptor of the convolution (padding, stride, etc.).
            grad_desc: descriptor of the backpropagated gradient
                       (same as for input vector during forward pass).
        """
        algo = cudnnffi.ffi.new("cudnnConvolutionBwdDataAlgo_t *")
        err = self._lib.cudnnGetConvolutionBackwardDataAlgorithm(
            self.handle, filter_desc, diff_desc, conv_desc, grad_desc,
            preference, memory_limit, algo)
        if err:
            raise CU.error("cudnnGetConvolutionBackwardDataAlgorithm", err)
        return int(algo[0])

    def get_convolution_backward_data_workspace_size(
            self, filter_desc, diff_desc, conv_desc, grad_desc, algo):
        """Returns required size of the additional temporary buffer
        for the specified backward data convolution algorithm.

        Parameters:
            filter_desc: descriptor of the convolutional kernels.
            diff_desc: descriptor of the error for backpropagation.
            conv_desc: descriptor of the convolution (padding, stride, etc.).
            grad_desc: descriptor of the backpropagated gradient
                       (same as for input vector during forward pass).
            algo: algorithm for the computing of backpropagated gradient.
        """
        size = cudnnffi.ffi.new("size_t *")
        err = self._lib.cudnnGetConvolutionBackwardDataWorkspaceSize(
            self.handle, filter_desc, diff_desc, conv_desc, grad_desc, algo,
            size)
        if err:
            raise CU.error("cudnnGetConvolutionBackwardDataWorkspaceSize",
                           err)
        return int(size[0])

    def convolution_backward_data(
            self, alpha, filter_desc, filter_data, diff_desc, diff_data,
            conv_desc, beta, grad_desc, grad_data,
            algo=None, workspace=None, workspace_size=0):
        """Computes backpropagated error.

        Parameters:
            alpha: diff_data multiplier (numpy array with one element).
            beta: grad_data multiplier (numpy array with one element).
            filter_data: convolutional kernels.
            diff_data: error for backpropagation.
            grad_data: backpropagated error.
        """
        if self.version < 4000:
            err = self._lib.cudnnConvolutionBackwardData(
                self.handle, CU.extract_ptr(alpha), filter_desc, filter_data,
                diff_desc, diff_data, conv_desc,
                CU.extract_ptr(beta), grad_desc, grad_data)
            if err:
                raise CU.error("cudnnConvolutionBackwardData", err)
            return
        if algo is None:
            # Get the algorithm
            algo = self.get_convolution_backward_data_algorithm(
                filter_desc, diff_desc, conv_desc, grad_desc,
                CUDNN_CONVOLUTION_BWD_DATA_SPECIFY_WORKSPACE_LIMIT
                if workspace_size else
                CUDNN_CONVOLUTION_BWD_DATA_NO_WORKSPACE, workspace_size)
        # Backpropagate the error with the selected algorithm
        err = self._lib.cudnnConvolutionBackwardData(
            self.handle, CU.extract_ptr(alpha), filter_desc, filter_data,
            diff_desc, diff_data, conv_desc,
            algo, 0 if workspace is None else workspace, workspace_size,
            CU.extract_ptr(beta), grad_desc, grad_data)
        if err:
            raise CU.error("cudnnConvolutionBackwardData", err)

    def pooling_forward(self, pooling_desc, alpha, src_desc, src_data,
                        beta, dest_desc, dest_data):
        """Does pooling forward propagation.

        Parameters:
            alpha: src_data multiplier (numpy array with one element).
            beta: dest_data multiplier (numpy array with one element).
        """
        err = self._lib.cudnnPoolingForward(
            self.handle, pooling_desc, CU.extract_ptr(alpha),
            src_desc, src_data,
            CU.extract_ptr(beta), dest_desc, dest_data)
        if err:
            raise CU.error("cudnnPoolingForward", err)

    def pooling_backward(self, pooling_desc, alpha, output_desc, output_data,
                         diff_desc, diff_data, input_desc, input_data,
                         beta, grad_desc, grad_data):
        """Does pooling backward propagation.

        Parameters:
            alpha: diff_data multiplier (numpy array with one element).
            beta: grad_data multiplier (numpy array with one element).
            output: output of the forward propagation.
            diff: error for backpropagation.
            input: input of the forward propagation.
            grad: backpropagated error.
        """
        err = self._lib.cudnnPoolingBackward(
            self.handle, pooling_desc, CU.extract_ptr(alpha),
            output_desc, output_data,
            diff_desc, diff_data, input_desc, input_data,
            CU.extract_ptr(beta), grad_desc, grad_data)
        if err:
            raise CU.error("cudnnPoolingBackward", err)

    def transform_tensor(self, alpha, src_desc, src_data,
                         beta, dest_desc, dest_data):
        """Transforms data from one layout to another
        (interleaved to splitted for example).

        Parameters:
            alpha: src_data multiplier (numpy array with one element).
            beta: dest_data multiplier (numpy array with one element).
        """
        err = self._lib.cudnnTransformTensor(
            self.handle, CU.extract_ptr(alpha), src_desc, src_data,
            CU.extract_ptr(beta), dest_desc, dest_data)
        if err:
            raise CU.error("cudnnTransformTensor", err)

    @property
    def dropout_states_size(self):
        size = cudnnffi.ffi.new("size_t *")
        err = self._lib.cudnnDropoutGetStatesSize(self.handle, size)
        if err:
            raise CU.error("cudnnDropoutGetStatesSize", err)
        return int(size[0])

    def _release(self):
        if self._lib is not None and self.handle is not None:
            self._lib.cudnnDestroy(self.handle)
            self._handle = None

    def __del__(self):
        if self.context.handle is None:
            raise SystemError("Incorrect destructor call order detected")
        self._release()
        self.context._del_ref(self)