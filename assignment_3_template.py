import datetime
import time
import hashlib
import random
import json
from fastecdsa import ecdsa, keys, curve, point

class Miner:
    def __init__(self):
        self.chain = [] # list of all the blocks

    def genesis_block(self):
        '''
        This is the first block of the block chain
        '''
        block = {
            'previous_hash': 00000000000000,
            'index': len(self.chain),
            'transactions': [],
            'bits': 0x1EFFFFFF,
            'nonce': 0,
            'time': str(datetime.datetime.now()),
        }
        return block

    def make_empty_block(self, bits):
        '''
        @param: bits is the value that is used to computer the difficulty
        as well as the target hash

        note: there is no hash in this block
        that will be added while mining
        '''
        previous_hash = self.chain[-1]['hash']
        block = {
            'previous_hash': previous_hash,
            'index': len(self.chain),
            'transactions': [],
            'bits': bits,
            'nonce': random.randint(0, 2**32),
            'time': str(datetime.datetime.now())
        }
        print(block)
        return block

    def hash(self, blob):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        """
        # We must make sure that the Dictionary is Ordered, or we may have inconsistent hashes
        block_string = json.dumps(blob, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine(self, block):
        '''
        @param: block - this is the block that we will
        preform proof of work on

        directions:
        1) get_target_from_bits(block["bits"])
        2) hash the block
        3) if the hash of the block is not less then the value from step 1
            change the block['nonce'] and try again
        4) repeat until you find a hash that is less then the target hash

        note: this is best done with a while loop
        note2: after debugging remove all prints, or mining will be too slow
        '''

        target = get_target_from_bits(block["bits"])
        target_temp = target
        target_temp_int = target

        while (target_temp_int >= target):
            target_temp = self.hash(block)
            target_temp_int = int(target_temp,16)
            block["nonce"] = random.randint(0, 2**32)
        
        block["hash"] = target_temp
        self.chain.append(block)
        return block

def pad_leading_zeros(hex_str):
    ''' 
    this function pads on the leading zeros
    this helps with readability of comparing hashes
    '''
    hex_num_chars = hex_str[2:]
    num_zeros_needed = 64 - len(hex_num_chars)
    padded_hex_str = '0x%s%s' % ('0' * num_zeros_needed, hex_num_chars)
    return padded_hex_str

def read_str_time(time):
    ''' 
    this function takes the time in string format
    and converts it to python datetime format
    '''
    return datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')

def datetime_to_seconds(time):
    ''' 
    this function takes the time in datetime format
    and returns the total number of seconds
    '''
    return time.total_seconds()


def get_target_from_bits(bits):
    ''' 
    this function takes the bits from the block
    and expands it into a 256-bit target

    eg
    bits = 0x1d00ffff
    divide bits into two parts
    part 1 = 0x1d
    part 2 = 0x00ffff

    0x00ffff * 2**(8*(0x1d - 3)) 
    = 0x00000000FFFF0000000000000000000000000000000000000000000000000000

    note: https://en.bitcoin.it/wiki/Difficulty
    note: see lecture 5 slides
    '''
    part_1 = (bits & 0xff000000) >> 24
    part_2 = (bits & 0x00ffffff)
    format(part_1, '#04x')
    format(part_2, '#08x')
    target = part_2 * 2**(8*(part_1 - 3))
    return target


def get_difficulty_from_bits(bits):
    '''
    this function calculates the bits
    '''
    difficulty_one_target = 0x00FFFFFF * 2 ** (8 * (0x1E - 3))
    target = get_target_from_bits(bits)
    calculated_difficulty = difficulty_one_target / float(target)
    return calculated_difficulty


def get_bits_from_target(target):
    '''
    this function gets the bits from the target
    this is the inverse of the get_target_from_bits()
    hints: bitlength = len(hex(target)[2:])*4
    '''
    target = hex(target)[2:]
    bitlength = len(target)*4
    if bitlength % 8 != 0:
        print(target)
        target = '0' + target
        bitlength = len(target)*4
    
    part_1 = target[0:6]
    part_2 = int((bitlength - 6 * 4) / 8 + 3)
    bits = (part_2 << 24) + int(part_1, 16)
    return bits


get_bits_from_target(get_target_from_bits(0x1effffff))
def change_target(prev_bits, start_time, end_time, target_time):
    '''
    @param prev_bits : this is previous bits value
    @param starting_time : this is the starting time of this difficulty
        NOTE: type is Datetime
    @param end_time : this is the end time of this difficulty
        NOTE: type is Datetime
    @param target_time : this is the time that we want the blocks to take to mine

    directions:
    1) take the bits and get the target
    2) get the time_span between end and start in seconds
        NOTE: there is a function for getting datetime in seconds
    3) multiply the target by the time_span
    4) divide the target by the target time

    '''
    new_target = get_target_from_bits(prev_bits)
    time_span = datetime_to_seconds((read_str_time(end_time) - read_str_time(start_time)))
    new_target = new_target * time_span
    new_target = int(new_target / target_time)
    return new_target


if __name__ == "__main__":
    '''
    this mines 144 blocks

    first it mines using difficulty 1
    then it mines and attempts to get an average time of 2 seconds
    then 4 seconds
    then 6 seconds
    and finally 10 seconds

    the average will never be exact,
    but in my testing i found it it typically not off by
    more than 1 second

    NOTE: on final run for accuracy please dont run any other programs
    '''

    # the time we want each block to take
    times = [2, 4, 6, 10]
    # the number of blocks to mine at each difficulty level
    number_of_blocks = 32

    # create the miner
    miner = Miner()
    # create the genesis block
    gen_block = miner.genesis_block()
    # mine the genesis block
    miner.mine(gen_block)

    # get the time for difficulty of 1
    for i in range(number_of_blocks):
        # get the bits
        bits = miner.chain[-1]["bits"]
        empty_block = miner.make_empty_block(bits) 
        miner.mine(empty_block)

    totaltime = datetime_to_seconds(read_str_time(miner.chain[number_of_blocks]["time"]) - read_str_time(miner.chain[0]["time"]))
    print("average time = {}".format(totaltime/number_of_blocks))
    print("difficulty = {}".format(get_difficulty_from_bits(bits)))


    for index, time in enumerate(times):
        target = change_target(bits, miner.chain[index*number_of_blocks]["time"], miner.chain[(index+1)*number_of_blocks]["time"], times[index]*number_of_blocks)
        bits = get_bits_from_target(target)

        for i in range(number_of_blocks):
            empty_block = miner.make_empty_block(bits) 
            miner.mine(empty_block)

        totaltime = datetime_to_seconds(read_str_time(miner.chain[(index+2)*number_of_blocks]["time"]) - read_str_time(miner.chain[(index+1)*number_of_blocks]["time"]))
        print("average time = {}".format(totaltime/number_of_blocks))
        print("difficulty = {}".format(get_difficulty_from_bits(bits)))

    with open('chain.json', 'w') as outfile:
        json.dump(miner.chain, outfile, sort_keys = True, indent = 4)
