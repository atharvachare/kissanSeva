import tensorflow as tf
import json
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.utils.class_weight import compute_class_weight

#config

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15
LR = 1e-3

#Data generators

def get_datagen(is_crop=False):
    if is_crop:
        return ImageDataGenerator(
            rescale=1./255,
            validation_split=0.2,
            rotation_range=45,
            zoom_range=0.4,
            brightness_range=[0.4, 1.6],
            shear_range=0.35,
            horizontal_flip=True,
            channel_shift_range=20
        )
    else:
        return ImageDataGenerator(
            rescale=1./255,
            validation_split=0.2,
            rotation_range=30,
            zoom_range=0.2,
            brightness_range=[0.6, 1.4],
            shear_range=0.2,
            horizontal_flip=True
        )

def get_generators(path, is_crop=False):
    datagen = get_datagen(is_crop)
    train = datagen.flow_from_directory(
        path,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training"
    )
    val = datagen.flow_from_directory(
        path,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation"
    )
    return train, val

#model builder

def build_model(num_classes):
    base = MobileNetV2(weights="imagenet", include_top=False,
                       input_shape=(224, 224, 3))
    base.trainable = False

    x = GlobalAveragePooling2D()(base.output)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.4)(x)
    out = Dense(num_classes, activation="softmax")(x)

    model = Model(base.input, out)
    model.compile(
        optimizer=Adam(LR),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model

callbacks = [
    EarlyStopping(patience=4, restore_best_weights=True),
    ReduceLROnPlateau(patience=2, factor=0.3)
]

#crop classifier

print("\nTraining Crop Classifier (Rice vs Wheat)")
crop_train, crop_val = get_generators("dataset/crop_classifier", is_crop=True)

# save correct label mapping
with open("crop_classes.json", "w") as f:
    json.dump(crop_train.class_indices, f)

class_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.unique(crop_train.classes),
    y=crop_train.classes
)
class_weights = dict(enumerate(class_weights))

crop_model = build_model(num_classes=2)
crop_model.fit(
    crop_train,
    validation_data=crop_val,
    epochs=EPOCHS,
    callbacks=callbacks,
    class_weight=class_weights
)
crop_model.save("crop_classifier.h5")

#rice Disease model

print("\nTraining Rice Disease Model")
rice_train, rice_val = get_generators("dataset/rice_diseases")

with open("rice_classes.json", "w") as f:
    json.dump(rice_train.class_indices, f)

rice_model = build_model(rice_train.num_classes)
rice_model.fit(
    rice_train,
    validation_data=rice_val,
    epochs=EPOCHS,
    callbacks=callbacks
)
rice_model.save("rice_disease_model.h5")

#Wheat Disease model

print("\nTraining Wheat Disease Model")
wheat_train, wheat_val = get_generators("dataset/wheat_diseases")

with open("wheat_classes.json", "w") as f:
    json.dump(wheat_train.class_indices, f)

wheat_model = build_model(wheat_train.num_classes)
wheat_model.fit(
    wheat_train,
    validation_data=wheat_val,
    epochs=EPOCHS,
    callbacks=callbacks
)
wheat_model.save("wheat_disease_model.h5")

print("\n✅ TRAINING COMPLETE")
