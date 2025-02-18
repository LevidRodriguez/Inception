import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
# import tensorflow as tf
import os
import urllib.request
from tensorflow.python.platform import gfile
import tarfile
import numpy as np

work_dir = ''

# Se descarga y descomprime el modelo Inception entrenado con la bd ImageNet
model_url = 'http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz'
file_name = model_url.split('/')[-1]
file_path = os.path.join(work_dir, file_name)

if not os.path.exists(file_path):
    file_path, _ = urllib.request.urlretrieve(model_url, file_path)
tarfile.open(file_path, 'r:gz').extractall(work_dir)

# El modelo en formato Protocol Buffers (protobuf) se lee como cadena y con tf.GraphDef se carga en memoria
model_path = os.path.join(work_dir, 'classify_image_graph_def.pb')
with gfile.FastGFile(model_path, 'rb') as f:
    graph_defnition = tf.GraphDef()
    graph_defnition.ParseFromString(f.read())

# La capa bottleneck pool_3/_reshape:0 es de 2,048 dimensiones
# El nombre del placeholder de entrada es DecodeJpeg/contents:0
# El nombre del tensor de entrada redimensionado es es ResizeBilinear:0
bottleneck, image, resized_input = (
    tf.import_graph_def(
        graph_defnition,
        name='',
        return_elements=['pool_3/_reshape:0',
                         'DecodeJpeg/contents:0',
                         'ResizeBilinear:0'])
)

# Cargue las imagenes en memoria
# query_image_path = os.path.join(work_dir, 'cat.1000.jpg')
# query_image_path = os.path.join(work_dir, 'DJI_0397.JPG')
query_image_path = os.path.join(work_dir, 'finalResult.jpg')
query_image = gfile.FastGFile(query_image_path, 'rb').read()
print (query_image_path)

# target_image_path = os.path.join(work_dir, 'cat.1001.jpg') # 16.99647
# target_image_path = os.path.join(work_dir, 'cropped_panda.jpg') # 20.412373
# target_image_path = os.path.join(work_dir, 'DJI_0698.JPG') # 12.741378, 11.564167
# target_image_path = os.path.join(work_dir, 'finalResult2.jpg') #11.793492
# target_image_path = os.path.join(work_dir, 'DJI_0331.JPG') #15.96557
target_image_path = os.path.join(work_dir, 'compare_transparent_mosaic_group1.jpg') #16.794645
target_image = gfile.FastGFile(target_image_path, 'rb').read()
print (target_image_path)

# Funcion que extrae las caracteristicas bottleneck de la image_data usando la sesion
def get_bottleneck_data(session, image_data):
    bottleneck_data = session.run(bottleneck, {image: image_data})
    bottleneck_data = np.squeeze(bottleneck_data)
    return bottleneck_data

# Inicie la sesion y pase las imagenes para realizar la inferencia y obtener los valores bottleneck
session = tf.Session()
query_feature = get_bottleneck_data(session, query_image)
print(query_feature)
target_feature = get_bottleneck_data(session, target_image)
print(target_feature)

# Calcule la distancia euclidiana entre las caracteristicas  
dist = np.linalg.norm(np.asarray(query_feature) - np.asarray(target_feature))
print("Distancia euclidiana entre las caracteristicas de las imagenes:  ", dist)
