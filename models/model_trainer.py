import argparse
import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from matplotlib import pyplot as plt
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split


def makeTrainTestSets(dataFrame: pd.DataFrame, testSize: float = 0.3, randomState: int = 42) -> tuple:
    classList = dataFrame.iloc[:, -1]
    convertor = LabelEncoder()
    y = convertor.fit_transform(classList)
    scaler = StandardScaler()
    X = scaler.fit_transform(np.array(dataFrame.iloc[:, :-1], dtype = float))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize, random_state=randomState)
    return X_train, X_test, y_train, y_test


def createModel(inputShape: int) -> keras.models.Sequential:
    model = keras.models.Sequential([
    keras.layers.Dense(512, activation='relu', input_shape=inputShape),
    keras.layers.Dropout(0.2),

    keras.layers.Dense(256, activation='relu'),
    keras.layers.Dropout(0.2),

    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dropout(0.2),

    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(0.2),

    keras.layers.Dense(10, activation='softmax')
    ])
    return model


def trainModel(model: keras.models.Sequential, epochs: int, learnRate: float, X_train, y_train, X_test, y_test):
    batch_size = 128
    optimizer = keras.optimizers.Adam(learning_rate=learnRate)
    model.compile(loss='sparse_categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    history = model.fit(X_train,
                        y_train,
                        batch_size=batch_size,
                        epochs=epochs,
                        validation_data=(X_test, y_test),
                        verbose=1)
    return history


def plotHistory(history, title, subtitle, filename=None):
    print(f"accuracy: {max(history.history['val_accuracy'])}")
    pd.DataFrame(history.history).plot(figsize=(12, 6))
    plt.grid(which='major', linestyle='-', linewidth='0.5', color='black')
    plt.grid(which='minor', linestyle=':', linewidth='0.5', color='gray')
    plt.minorticks_on()
    plt.gca().set_ylim(0, 2)
    plt.suptitle(title)
    plt.title(subtitle)
    if filename:
        plt.savefig(filename)
    else:
        plt.show()


def modelEvaluator(model, X_test, y_test):
    test_loss, test_acc = model.evaluate(X_test, y_test)
    print(f"Test accuracy: {test_acc}")
    print(f"Test loss: {test_loss}")
    return test_acc, test_loss


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, required=True)
    parser.add_argument('--epochs', type=int, required=True)
    parser.add_argument('--learnrate', type=float, required=True)
    parser.add_argument('--makegraph', type=bool)
    args = parser.parse_args()

    data = pd.read_csv(args.data)
    data = data.dropna()
    data = data.drop(data.columns[0], axis=1)
    X_train, X_test, y_train, y_test = makeTrainTestSets(data)
    model = createModel(X_train.shape[1:])
    gpus = tf.config.list_physical_devices('GPU')
    print(f"Num GPUs Available: {len(gpus)}")
    history = trainModel(model, args.epochs, args.learnrate, X_train, y_train, X_test, y_test)
    modelEvaluator(model, X_test, y_test)
    dataFileName = args.data.split('/')[-1].strip('.csv')
    graphTitle = f"Accuracy and Loss for {dataFileName} dataset"
    graphSubtitle = f"Learning Rate: {args.learnrate} over {args.epochs} Epochs"
    if args.makegraph:
        graphFilename = f"accuLoss{dataFileName}_{args.learnrate}lr_{args.epochs}e.png"
        plotHistory(history, graphTitle, graphSubtitle, graphFilename)
    else:
        plotHistory(history, graphTitle, graphSubtitle)


if __name__ == '__main__':
    main()
