import osimport imageio as iofrom keras.callbacks import TensorBoard, ModelCheckpointfrom sklearn.model_selection import train_test_splitfrom util import *np.random.seed(42)os.environ["CUDA_VISIBLE_DEVICES"] = "0"data_location = ''training_images_loc = data_location + 'Drive/train/images/'training_label_loc = data_location + 'Drive/train/labels/'train_files = os.listdir(training_images_loc)train_data = []train_label = []# 预处理数据desired_size = 592  # 期望的resolutionfor i in train_files:    im = io.imread(training_images_loc + i)    label = io.imread(training_label_loc + i.split('_')[0] + '_manual1.png',                      pilmode="L")  # ‘L’ (8-bit pixels, grayscale)    old_size = im.shape[:2]  # old_size is in (height, width) format    delta_w = desired_size - old_size[1]    delta_h = desired_size - old_size[0]    # 图片上下左右扩容的pixel值,不对半分二是减是因为奇数，//：floor除    top, bottom = delta_h // 2, delta_h - (delta_h // 2)    left, right = delta_w // 2, delta_w - (delta_w // 2)    # 输入三通道, 输出单通道    color = [0, 0, 0]    color2 = [0]    # BORDER_CONSTANT 常数填充，上面颜色为黑色    # https://bit.ly/39JbjHG    new_im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT,                                value=color)    new_label = cv2.copyMakeBorder(label, top, bottom, left, right, cv2.BORDER_CONSTANT,                                   value=color2)    # 127:阈值; 255：超过阈值填充色;    _, temp = cv2.threshold(new_label, 127, 255, cv2.THRESH_BINARY)    train_data.append(cv2.resize(new_im, (desired_size, desired_size)))    train_label.append(cv2.resize(temp, (desired_size, desired_size)))train_data = np.array(train_data)train_label = np.array(train_label)x_train = train_data.astype('float32') / 255.y_train = train_label.astype('float32') / 255.x_rotated, y_rotated, x_flipped, y_flipped = img_augmentation(x_train, y_train)  # 生成60张翻转，20张旋转x_train = np.concatenate([x_train, x_rotated, x_flipped])y_train = np.concatenate([y_train, y_rotated, y_flipped])x_train, x_validate, y_train, y_validate = train_test_split(x_train, y_train, test_size=0.10,                                                            random_state=101)  # 划分训练集和测试集# todo 这里为什么还要reshape，shape不是满足了吗？x_train = np.reshape(x_train, (len(x_train), desired_size, desired_size, 3))  # adapt this if using `channels_first` image data formaty_train = np.reshape(y_train, (len(y_train), desired_size, desired_size, 1))  # adapt this if using `channels_first` imx_validate = np.reshape(x_validate, (len(x_validate), desired_size, desired_size, 3))  # adapt this if using `channels_first` image data formaty_validate = np.reshape(y_validate,                        (len(y_validate), desired_size, desired_size, 1))  # adapt this if using `channels_first` imTensorBoard(log_dir='./autoencoder', histogram_freq=0,            write_graph=True, write_images=True)for i in range(80, 95):    i = i / 100    print(i)    from CARUNet import *    model = CARUNet(input_size=(desired_size, desired_size, 3), start_neurons=16, keep_prob=i, lr=1e-3)    weight = "Drive/Model/CARUNet" + str(i) + ".h5"    restore = False    if restore and os.path.isfile(weight):        model.load_weights(weight)    model_checkpoint = ModelCheckpoint(weight, monitor='val_accuracy', verbose=1, save_best_only=False)    history = model.fit(x_train, y_train,                        epochs=100,                        batch_size=2,                        # validation_split=0.05,                        validation_data=(x_validate, y_validate),                        shuffle=True,                        callbacks=[TensorBoard(log_dir='./autoencoder'), model_checkpoint])