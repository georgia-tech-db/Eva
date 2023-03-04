# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from abc import abstractmethod

class EvaArgument(object):
    """
    Base class for the data types that are used inside Eva. This class is inherited by the NumPyArray, 
    PyTorchTensor and PandasDataFrame classes. 
    The functions are implemented in the child classes. 
    
    """
    
    @abstractmethod
    def __init__(self, shape=None, dtype=None, columns=None) -> None:
        """The parameters like shape, data type are passed as parameters to be initialized
        
        Args:
            shape (tuple[int]): a tuple of integers of the required shape.
            dtype (str): datatype of the elements. Types are int32, float16 and float32.
            
        """
        pass

    @abstractmethod
    def check_type(self, input_object) -> bool:
        """Checks the type of the input_object with 
        
        Args:
            input_object (any): the object whose type should be checked. The required type is given in the constructor.
        
        Returns:
            bool: True if the type of input_object matches the required type. False otherwise.

        """
        pass

    def check_shape(self, input_object, required_shape) -> bool:
        """Checks the shape of the input_object with 
        
        Args:
            input_object (any): the object whose shape should be checked. The required shape is given in the constructor. 
        
        Returns:
            bool: True if the shape of input_object matches the required type. False otherwise.

        """
        
        pass

    def name(self):
        """Returns the name of the EvaArgument. 
        
        It is used in the construction of the error messages.
        """
        pass

    def is_output_columns_set(self):
        """Checks if the output columns are set. 
        
        This is used for EvaArguments which are of PandasDataFrame type.
        
        """
        pass

    def check_column_names(self, output_object):
        """Checks if the output column names match the required column names list.
        
        Args:
            output_object (any): the object whose columns should be checked. It should be of type PandasDataFrame.
                        The required column list is given in the constructor. 
        
        Returns:
            bool: True if the column names of output_object matches the required columns list. False otherwise.
        
        """
        pass
