import os 
import urllib.request as request 
from zipfile import ZipFile
import tensorflow as tf
from pathlib import Path
from poxVisionDetection.entity.config_entity import PrepareBaseModelConfig

class PrepareBaseModel:
    def __init__(self, config : PrepareBaseModelConfig):
        self.config = config

    def get_base_model(self):
        self.model              = tf.keras.applications.ResNet50(
            include_top         = self.config.params_include_top,
            weights             = self.config.params_weight,
            input_shape         = self.config.params_image_size,
        )

        # THE BASE MODEL WILL GET SAVED IN THE PATH PROVIDED
        self.save_model(path    = self.config.base_model_path,
                        model   = self.model)

    # THE WEIGHTS THAT ARE PRESENT IN THE ResNet50 MODEL ARE GOING TO BE USED AS SUCH ONLY THE INPUT AND OUTPUT LAYERS ARE GOING TO BE TRAINED
    @staticmethod
    def _prepare_full_model(model, classes, freeze_all, freeze_till, learning_rate):
        if freeze_all:
            for layer in model.layers:
                model.trainable = False
        elif(freeze_till is not None) and (freeze_till > 0):
            for layer in model.layers[:-freeze_till]:
                model.trainable = False

        flatten = model.output

        Globalavgpool2D   = tf.keras.layers.GlobalAveragePooling2D()(flatten)

        Dlayer1            = tf.keras.layers.Dense(
            units           = 64,
            activation      = 'relu'
        )(Globalavgpool2D)

        pred_layer            = tf.keras.layers.Dense(
            units           = classes,
            activation      = 'softmax'
        )(Dlayer1)

        full_model        = tf.keras.models.Model(
            inputs          = model.input,
            outputs         = pred_layer
        )

        print(full_model)
        print('-------------------------------------------')

        full_model.compile(
            optimizer           = tf.keras.optimizers.SGD(learning_rate = learning_rate),
            loss                = tf.keras.losses.CategoricalCrossentropy(),
            metrics             = ['accuracy']
        )

        full_model.summary()
        return full_model

    def updated_base_model(self):
        self.full_model        = self._prepare_full_model(
            model              = self.model,
            classes            = self.config.params_classes,
            freeze_all         = True,
            freeze_till        = None,
            learning_rate      = self.config.params_learning_rate
        )

        self.save_model(path   = self.config.updated_base_model_path,
                        model  = self.full_model)

    @staticmethod
    def save_model(path : Path, model : tf.keras.Model):
        print(model.summary)
        model.save(path)