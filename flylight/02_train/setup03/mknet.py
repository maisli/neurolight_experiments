from gunpowder.zoo.tensorflow import unet, conv_pass
import tensorflow as tf
import json
import sys
import os

def create_network(input_shape, name, output_folder):

    tf.reset_default_graph()
    
    # c=3, d, h, w
    raw = tf.placeholder(tf.float32, shape=(3,) + input_shape)
    
    # b=1, c=3, d, h, w
    raw_batched = tf.reshape(raw, (1, 3,) + input_shape)

    out = unet(raw_batched, 12, 5, [[2,2,2],[2,2,2],[2,2,2]])
    output_batched = conv_pass(
            out,
            kernel_size=1,
            num_fmaps=1,
            num_repetitions=1,
            activation='sigmoid')
    output_shape_batched = output_batched.get_shape().as_list()

    # d, h, w
    output_shape = output_shape_batched[2:]
    output = tf.reshape(output_batched, output_shape)

    gt = tf.placeholder(tf.float32, shape=output_shape)
    loss_weights = tf.placeholder(tf.float32, shape=output_shape)

    loss = tf.losses.mean_squared_error(
            gt,
            output,
            loss_weights)

    opt = tf.train.AdamOptimizer(
            learning_rate=0.5e-4,
            beta1=0.95,
            beta2=0.999,
            epsilon=1e-8)
    optimizer = opt.minimize(loss)

    print("input shape: %s"%(input_shape,))
    print("output shape: %s"%(output_shape,))

    tf.train.export_meta_graph(filename=os.path.join(output_folder, name + '.meta'))

    names = {
            'raw': raw.name,
            'pred': output.name,
            'gt': gt.name,
            'loss_weights': loss_weights.name,
            'loss': loss.name,
            'optimizer': optimizer.name,
    }
    with open(os.path.join(output_folder, name + '_names.json'), 'w') as f:
        json.dump(names, f)

    config = {
            'input_shape': input_shape,
            'output_shape': output_shape,
            'out_dims': 1
    }
    with open(os.path.join(output_folder, name + '_config.json'), 'w') as f:
        json.dump(config, f)

if __name__ == "__main__":

    root = '/groups/kainmueller/home/maisl/workspace/neurolight/experiments'
    experiment = 'setup03_030419_00'

    if len(sys.argv) > 1:
        experiment = sys.argv[1]
    if len(sys.argv) > 2:
        root = sys.argv[2]

    output_folder = os.path.join(root, experiment, 'train')
    try:
        os.makedirs(output_folder)
    except OSError:
        pass

    #create_network((128, 128, 128), 'train_net', output_folder)
    create_network((180, 180, 180), 'test_net', output_folder)
