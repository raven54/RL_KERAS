
import tensorflow as tf
import numpy as np
import time

class Model:
    def __init__(self, sess, name, class_num):
        self.sess = sess
        self.name = name
        self.class_num = class_num
        self._build_net()

    def _build_net(self):
        with tf.variable_scope(self.name):
            with tf.name_scope('input_layer') as scope:

                self.dropout_rate = tf.Variable(tf.constant(value=0.5), name='dropout_rate')
                self.training = tf.placeholder(tf.bool, name='training')

                self.X = tf.placeholder(tf.float32, [None, 144*144], name='x_data')
                X_img = tf.reshape(self.X, shape=[-1, 144, 144, 1])
                self.Y = tf.placeholder(tf.float32, [None, self.class_num], name='y_data')

            with tf.name_scope('conv_layer1') as scope:
                self.W1_sub = tf.get_variable(name='W1_sub', shape=[4, 4, 1, 20], dtype=tf.float32, initializer=tf.contrib.layers.xavier_initializer_conv2d())
                self.L1_sub = tf.nn.conv2d(input=X_img, filter=self.W1_sub, strides=[1, 1, 1, 1], padding='VALID')  # 144x144 -> 141x141
                self.L1_sub = self.BN(input=self.L1_sub, scale= True,  training=self.training, name='Conv1_sub_BN')
                self.L1_sub = self.parametric_relu(self.L1_sub, 'R1_sub')

                self.W2_sub = tf.get_variable(name='W2_sub', shape=[4, 4, 20, 20], dtype=tf.float32, initializer=tf.contrib.layers.xavier_initializer_conv2d())
                self.L2_sub = tf.nn.conv2d(input=self.L1_sub, filter=self.W2_sub, strides=[1, 1, 1, 1], padding='VALID')  # 141x141 -> 138x138
                self.L3_sub = self.BN(input=self.L2_sub, scale=True, training=self.training, name='Conv2_sub_BN')
                self.L2_sub = self.parametric_relu(self.L2_sub, 'R2_sub')

                self.W3_sub = tf.get_variable(name='W3_sub', shape=[3, 3, 20, 20], dtype=tf.float32, initializer=tf.contrib.layers.xavier_initializer_conv2d())
                self.L3_sub = tf.nn.conv2d(input=self.L2_sub, filter=self.W3_sub, strides=[1, 1, 1, 1], padding='VALID')  # 138x138 -> 136x136
                self.L3_sub = self.BN(input=self.L3_sub, scale=True, training=self.training, name='Conv3_sub_BN')
                self.L3_sub = self.parametric_relu(self.L3_sub, 'R3_sub')

                # self.L1 = tf.nn.lrn(self.L3_sub, depth_radius=5, bias=2, alpha=0.0001, beta=0.75, name='LRN1')
                self.L1 = tf.nn.max_pool(value=self.L3_sub, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')  # 136x136 -> 68x68
                # self.L1 = tf.layers.dropout(inputs=self.L1, rate=self.dropout_rate, training=self.training)


            with tf.name_scope('conv_layer2') as scope:
                self.W2 = tf.get_variable(name='W2', shape=[3, 3, 20, 40], dtype=tf.float32, initializer=tf.contrib.layers.xavier_initializer_conv2d())
                self.L2 = tf.nn.conv2d(input=self.L1, filter=self.W2, strides=[1, 1, 1, 1], padding='SAME')
                self.L2 = self.BN(input=self.L2, scale=True, training=self.training, name='Conv2_BN')
                self.L2 = self.parametric_relu(self.L2, 'R2')

                # self.L2 = tf.nn.lrn(self.L2, depth_radius=5, bias=2, alpha=0.0001, beta=0.75, name='LRN2') # Local Response Normalization 구현
                self.L2 = tf.nn.max_pool(value=self.L2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')  # 68x68 -> 34x34
                # self.L2 = tf.layers.dropout(inputs=self.L2, rate=self.dropout_rate, training=self.training)


            with tf.name_scope('conv_layer3') as scope:
                self.W3 = tf.get_variable(name='W3', shape=[3, 3, 40, 80], dtype=tf.float32, initializer=tf.contrib.layers.xavier_initializer_conv2d())
                self.L3 = tf.nn.conv2d(input=self.L2, filter=self.W3, strides=[1, 1, 1, 1], padding='SAME')
                self.L3 = self.BN(input=self.L3, scale=True, training=self.training, name='Conv3_BN')
                self.L3 = self.parametric_relu(self.L3, 'R3')
                self.L3 = tf.nn.max_pool(value=self.L3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')  # 34x34 -> 17x17
                # self.L3 = tf.layers.dropout(inputs=self.L3, rate=self.dropout_rate, training=self.training)


            with tf.name_scope('conv_layer4') as scope:
                self.W4 = tf.get_variable(name='W4', shape=[2, 2, 80, 160], dtype=tf.float32, initializer=tf.contrib.layers.xavier_initializer_conv2d())
                self.L4 = tf.nn.conv2d(input=self.L3, filter=self.W4, strides=[1, 1, 1, 1], padding='VALID')
                self.L4 = self.BN(input=self.L4, scale=True, training=self.training, name='Conv4_sub_BN')
                self.L4 = self.parametric_relu(self.L4, 'R4')
                self.L4 = tf.nn.max_pool(value=self.L4, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')  # 16x16 -> 8x8
                # self.L4 = tf.layers.dropout(inputs=self.L4, rate=self.dropout_rate, training=self.training)
                # self.L4 = tf.reshape(self.L4, shape=[-1, 8 * 8 * 160])


            with tf.name_scope('conv_layer5') as scope:
                self.W5 = tf.get_variable(name='W5', shape=[7, 7, 160, 320], dtype=tf.float32, initializer=tf.contrib.layers.xavier_initializer_conv2d())
                self.L5 = tf.nn.conv2d(input=self.L4, filter=self.W5, strides=[1, 1, 1, 1], padding='SAME')
                self.L5 = self.BN(input=self.L5, scale=True, training=self.training, name='Conv5_sub_BN')
                self.L5 = self.parametric_relu(self.L5, 'R5')
                self.L5 = tf.nn.max_pool(value=self.L5, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')  # 8x8 -> 4x4
                # self.L5 = tf.layers.dropout(inputs=self.L5, rate=self.dropout_rate, training=self.training)
                self.L5 = tf.reshape(self.L5, shape=[-1, 4 * 4 * 320])


            with tf.name_scope('fc_layer1') as scope:
                self.W_fc1 = tf.get_variable(name='W_fc1', shape=[4 * 4 * 320, 1000], dtype=tf.float32, initializer=tf.contrib.layers.variance_scaling_initializer())
                self.b_fc1 = tf.Variable(tf.constant(value=0.001, shape=[1000], name='b_fc1'))
                self.L6 = tf.matmul(self.L5, self.W_fc1) + self.b_fc1
                self.L6 = self.BN(input=self.L6, scale=True, training=self.training, name='Conv6_sub_BN')
                self.L_fc1 = self.parametric_relu(self.L6, 'R_fc1')
                # self.L_fc1 = tf.layers.dropout(inputs=self.L_fc1, rate=self.dropout_rate, training=self.training)


            with tf.name_scope('fc_layer2') as scope:
                self.W_fc2 = tf.get_variable(name='W_fc2', shape=[1000, 1000], dtype=tf.float32, initializer=tf.contrib.layers.variance_scaling_initializer())
                self.b_fc2 = tf.Variable(tf.constant(value=0.001, shape=[1000], name='b_fc2'))
                self.L7 = tf.matmul(self.L_fc1, self.W_fc2) + self.b_fc2
                self.L7 = self.BN(input=self.L7, scale=True, training=self.training, name='Conv7_sub_BN')
                self.L_fc2 = self.parametric_relu(self.L7, 'R_fc2')
                # self.L_fc2 = tf.layers.dropout(inputs=self.L_fc2, rate=self.dropout_rate, training=self.training)


            self.W_out = tf.get_variable(name='W_out', shape=[1000, self.class_num], dtype=tf.float32, initializer=tf.contrib.layers.variance_scaling_initializer())
            self.b_out = tf.Variable(tf.constant(value=0.001, shape=[self.class_num], name='b_out'))
            self.logits = tf.matmul(self.L_fc2, self.W_out) + self.b_out


        self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.logits, labels=self.Y)) \
                    + (0.01/(2*tf.to_float(tf.shape(self.Y)[0])))*tf.reduce_sum(tf.square(self.W_out))
        self.optimizer = tf.train.RMSPropOptimizer(learning_rate=0.0025,
                                                   momentum=0.9, decay=0.99,
                                                   epsilon=0.01).minimize(self.cost)

        # self.optimizer = tf.train.AdamOptimizer(learning_rate=0.005).minimize(self.cost)

        self.accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.arg_max(self.logits, 1), tf.arg_max(self.Y, 1)), dtype=tf.float32))

        # self.tensorflow_summary()


    def tensorflow_summary(self):
        self.W1_hist = tf.summary.histogram('W1_conv1', self.W1)
        self.b1_hist = tf.summary.histogram('b1_conv1', self.b1)
        self.L1_hist = tf.summary.histogram('L1_conv1', self.L1)

        self.W2_hist = tf.summary.histogram('W2_conv2', self.W2)
        self.b2_hist = tf.summary.histogram('b2_conv2', self.b2)
        self.L2_hist = tf.summary.histogram('L2_conv2', self.L2)

        self.W3_hist = tf.summary.histogram('W3_conv3', self.W3)
        self.b3_hist = tf.summary.histogram('b3_conv3', self.b3)
        self.L3_hist = tf.summary.histogram('L3_conv3', self.L3)

        self.W4_hist = tf.summary.histogram('W4_conv4', self.W4)
        self.b4_hist = tf.summary.histogram('b4_conv4', self.b4)
        self.L4_hist = tf.summary.histogram('L4_conv4', self.L4)

        self.W5_hist = tf.summary.histogram('W5_conv5', self.W5)
        self.b5_hist = tf.summary.histogram('b5_conv5', self.b5)
        self.L5_hist = tf.summary.histogram('L5_conv5', self.L5)

        self.W_fc1_hist = tf.summary.histogram('W6_fc1', self.W_fc1)
        self.b_fc1_hist = tf.summary.histogram('b6_fc1', self.b_fc1)
        self.L_fc1_hist = tf.summary.histogram('L6_fc1', self.L_fc1)

        self.W_fc2_hist = tf.summary.histogram('W6_fc2', self.W_fc2)
        self.b_fc2_hist = tf.summary.histogram('b6_fc2', self.b_fc2)
        self.L_fc2_hist = tf.summary.histogram('L6_fc2', self.L_fc2)

        self.cost_hist = tf.summary.scalar(self.name+'/cost_hist', self.cost)
        self.accuracy_hist = tf.summary.scalar(self.name+'/accuracy_hist', self.accuracy)

        # ※ merge_all 로 하는 경우, hist 를 모으지 않는 변수들도 대상이 되어서 에러가 발생한다.
        #    따라서 merge 로 모으고자하는 변수를 각각 지정해줘야한다.
        self.merged = tf.summary.merge([self.W1_hist, self.b1_hist, self.L1_hist,
                                        self.W2_hist, self.b2_hist, self.L2_hist,
                                        self.W3_hist, self.b3_hist, self.L3_hist,
                                        self.W4_hist, self.b4_hist, self.L4_hist,
                                        self.W5_hist, self.b5_hist, self.L5_hist,
                                        self.W_fc1_hist, self.b_fc1_hist, self.L_fc1_hist,
                                        self.W_fc2_hist, self.b_fc2_hist, self.L_fc2_hist,
                                        self.cost_hist, self.accuracy_hist])

    def predict(self, x_test):
        return self.sess.run(self.logits, feed_dict={self.X: x_test, self.training: False})

    def get_accuracy(self, x_test, y_test):
        return self.sess.run(self.accuracy, feed_dict={self.X: x_test, self.Y: y_test, self.training: False})

    def train(self, x_data, y_data):
        return self.sess.run([self.cost, self.optimizer], feed_dict={self.X: x_data, self.Y: y_data, self.training: True})


    def parametric_relu(self, _x, name):
        alphas = tf.get_variable(name,
                                 _x.get_shape()[-1],
                                 initializer=tf.constant_initializer(0.01),
                                 dtype=tf.float32)
        pos = tf.nn.relu(_x)
        neg = alphas * (_x - abs(_x)) * 0.5
        return pos + neg


    def max_out(self, inputs, num_units, axis=None):
        shape = inputs.get_shape().as_list()
        if shape[0] is None:
            shape[0] = -1
        if axis is None:  # Assume that channel is the last dimension
            axis = -1
        num_channels = shape[axis]
        if num_channels % num_units:
            raise ValueError(
                'number of features({}) is not a multiple of num_units({})'.format(num_channels, num_units))
        shape[axis] = num_units  # m
        shape += [num_channels // num_units]  # k
        outputs = tf.reduce_max(tf.reshape(inputs, shape), -1, keep_dims=False)
        return outputs

    def BN(self, input, training, scale, name, decay=0.99):
        return tf.contrib.layers.batch_norm(input, decay=decay, scale=scale, is_training=training, updates_collections=None, scope=name)

    