import TextualData.TextualData
import LSTM.lstm as lstm
import numpy as np
import torch.nn as nn
import torch.optim as optim
import torch
import time
from torch.autograd import Variable

text = TextualData.TextualData.TextualData(path='data/full_shak_eng.txt')

def generate(model, inp='#', temp = 0.7, my_len = 150):
    row = inp
    tensor_string = text.string_to_tensor(row)
    model.init_hidden()
    for i in range(len(tensor_string)):
        output = model.forward(tensor_string[i])
    row += text.alphabet[torch.multinomial(output.data.view(-1).div(temp).exp(),1)[0]]
    for i in range(my_len):
        output= model.forward(text.string_to_tensor(row)[-1])
        row += text.alphabet[torch.multinomial(output.data.view(-1).div(temp).exp(),1)[0]]
    return row

hidden_size = 64
#rnn = LSTMmodel(alpha_len, hidden_size)
rnn = lstm.LSTMmodel(hidden_s=hidden_size, input_s=text.alpha_len, n_layers=3)
rnn.optimizer = optim.Adam(rnn.parameters(), lr=0.004)
batch_size = 10
string_len = 25

print_every = 5
tot_loss=0
t = time.time()
print text.train_len

for epochs in range(10):
    index = 0
    done_batches = 0
    rnn.init_hidden()
    while index < text.test_len+string_len*batch_size:

        my_loss = rnn.train(text.get_batch(string_len,batch_size,index,1))
        index += string_len*batch_size
        done_batches += 1
        tot_loss += my_loss.data[0]
        if done_batches%print_every == 0:
            print epochs, '-', done_batches, '=' *  int(10 *tot_loss / print_every), tot_loss / print_every
            tot_loss = 0

            #torch.save(rnn.state_dict(), 'models/LSTM_'+str(i)+'.md')

    print 'valid loss', np.mean([rnn.loss_func(rnn.forward(inp), tar) for inp, tar in text.get_random_valid_batch(string_len,500,1)]).data[0]
    print generate(rnn)
print time.time()-t