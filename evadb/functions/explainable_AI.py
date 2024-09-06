# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from collections import OrderedDict
from evadb.functions.decorators.decorators import  setup, forward
import pandas as pd

from evadb.functions.abstract.pytorch_abstract_function import (
    PytorchAbstractClassifierFunction
)
from evadb.functions.abstract.abstract_function import (
    AbstractFunction
)
from evadb.utils.generic_utils import try_to_import_torch, try_to_import_torchvision
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from evadb.catalog.catalog_type import NdArrayType
from torchvision.transforms import Compose, Resize, ToTensor
import torch 
import torch.nn as nn 
from evadb.parser.types import FileFormatType
import copy
import numpy as np 





class ExplainableAI(AbstractFunction):
    @property
    def name(self) -> str:
        return "ExplainableAI"
    
    @setup(cacheable=True, function_type="ExplainableAI", batchable=True)
    def setup(self):
        try_to_import_torch()
        try_to_import_torchvision()
    
        self.hidden_storage= []
        model_urls = {
            "mnist": "http://ml.cs.tsinghua.edu.cn/~chenxi/pytorch-models/mnist-b07bb66b.pth"  # noqa
        }

        # https://github.com/aaron-xichen/pytorch-playground/blob/master/
        class MLP(nn.Module):
            def __init__(self, input_dims, n_hiddens, n_class):
                super(MLP, self).__init__()
                assert isinstance(input_dims, int), "Please provide int for input_dims"
                self.input_dims = input_dims
                current_dims = input_dims
                layers = OrderedDict()

                if isinstance(n_hiddens, int):
                    n_hiddens = [n_hiddens]
                else:
                    n_hiddens = list(n_hiddens)
                for i, n_hidden in enumerate(n_hiddens):
                    layers["fc{}".format(i + 1)] = nn.Linear(current_dims, n_hidden)
                    layers["relu{}".format(i + 1)] = nn.ReLU()
                    layers["drop{}".format(i + 1)] = nn.Dropout(0.2)
                    current_dims = n_hidden
                layers["out"] = nn.Linear(current_dims, n_class)

                self.model = nn.Sequential(layers)

            def forward(self, input):
                input = input.view(input.size(0), -1)
                assert input.size(1) == self.input_dims
                return self.model.forward(input)
    
        def mnist(input_dims=784, n_hiddens=[256, 256], n_class=10, pretrained=None):
            model = MLP(input_dims, n_hiddens, n_class)
            import torch.utils.model_zoo as model_zoo

            if pretrained is not None:
                m = model_zoo.load_url(
                    model_urls["mnist"], map_location=torch.device("cpu")
                )
                state_dict = m.state_dict() if isinstance(m, nn.Module) else m
                assert isinstance(state_dict, (dict, OrderedDict)), type(state_dict)
                model.load_state_dict(state_dict)
            return model

        self.model = mnist(pretrained=True)
        self.model.eval()
        
   

 
    @property
    def labels(self):
        return list([str(num) for num in range(10)])

    def transform(self, images):
        from PIL import Image
        from torchvision.transforms import Compose, Grayscale, Normalize, ToTensor

        composed = Compose(
            [
                Grayscale(num_output_channels=1),
                ToTensor(),
                Normalize((0.1307,), (0.3081,)),
            ]
        )
        # reverse the channels from opencv
        return composed(Image.fromarray(images[:, :, ::-1])).unsqueeze(0)
    
    
    
    
    def tsne(self, outcome) -> pd.DataFrame: 
        import matplotlib.pyplot as plt
        import numpy as np
        from sklearn.manifold import TSNE
        import matplotlib.pyplot as plt
        from matplotlib import cm

        # Reduce dimensions using t-SNE
        num_arrays = len(outcome)
        array_shape = (num_arrays, -1)  # -1 means NumPy will automatically calculate the size of the second dimension

        # Stack the arrays and reshape dynamically
        embedding = np.vstack([ i["embedding"] for i in outcome]).reshape(array_shape)
        label = np.vstack([ i["label"] for i in outcome]).reshape(-1)
        label = np.array([ i for i in label])
        print(label)
        tsne = TSNE(n_components=2, random_state=42)
        embedded_features = tsne.fit_transform(embedding)
        cmap = cm.get_cmap('tab20')
        fig, ax = plt.subplots(figsize=(6, 6))
        num_categories = 10
        for lab in range(num_categories):
            indices = (label == lab)
            print(indices)
            ax.scatter(embedded_features[indices, 0], embedded_features[indices, 1],
                        c=np.array(cmap(lab)).reshape(1, 4), label=lab,
                        s=2, alpha=0.6)

        ax.legend( markerscale=3)
        plt.show() 
        
        
    @forward(
        input_signatures=[    
            PandasDataframe(
                columns=["id"],
                column_types=[ NdArrayType.FLOAT32],
                column_shapes=[(None, None, 3)],
            )
         ],
        output_signatures=[
          PandasDataframe(
            columns=["status", "aggregate_results"],
            column_types=[
            # FileFormatType.IMAGE,
                NdArrayType.FLOAT32,  NdArrayType.FLOAT32
            ],
            column_shapes=[(None, None, 3), (None, None, 3)],
        )
        ],
         )
    def forward(self, frames) -> pd.DataFrame: 
        def extract_features(model, dataset):
            features = []
            new_model = copy.deepcopy(model)
            new_model = torch.nn.Sequential(*list(new_model.children())[:-2])
            for images in dataset:
                with torch.no_grad():
                    features.append(model(images).squeeze())
            return features
        
        # print(frames)
        np_data = np.array(frames.data)
        new_frame= []
        for data in np_data:
            new_frame += [self.transform(data)]
        # print(len(new_frame))
        labels = []
        for images in new_frame:
            prediction = self.model(images)
            label = prediction.data.argmax()
            labels.append(int(label))
        
        
        features = extract_features(self.model,new_frame)   
        
        outcome = []
        for feature, label  in zip(features, labels):
            outcome.append({"embedding": feature, "label": label})
        # print(outcome)
        self.tsne(outcome)
        
        
        # print loss lanscape
        import loss_landscapes
        import loss_landscapes.metrics
        import matplotlib.pyplot as plt
        STEPS = 40
        labels = torch.tensor(labels)
        print(labels.shape)
        new_frame = torch.stack(new_frame)
        new_frame = new_frame.squeeze()
        print(new_frame.shape)
        metric = loss_landscapes.metrics.Loss(torch.nn.CrossEntropyLoss(), new_frame, labels)
        loss_data_fin = loss_landscapes.random_plane(self.model, metric, 10, STEPS, normalization='filter', deepcopy_model=True)
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        X = np.array([[j for j in range(STEPS)] for i in range(STEPS)])
        Y = np.array([[i for _ in range(STEPS)] for i in range(STEPS)])
        ax.plot_surface(X, Y, loss_data_fin, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
        ax.set_title('Surface Plot of Loss Landscape')
        fig.show()
        
        return pd.DataFrame([{"status": "success"}], columns=["status", "aggregate_results"])
