# import libraries

import datetime
import hashlib
import json
from flask import Flask, jsonify

# 1. Blockchain (Server)
class Blockchain:

    def __init__(self):
        self.chain = []
        # genesis block
        self.create_block(proof = 1, prev_hash = '0', proof_of_work = None)

    def create_block(self, proof, prev_hash, proof_of_work):
        block = {
            'id_block': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prev_hash': prev_hash,
            # 'hash': hash_block,
            'proof_of_work': proof_of_work,
            'data': None
        }
        self.chain.append(block)
        return block

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof, hash_operation
    
    def get_hash(self, block):
        hash_operation = hashlib.sha256(json.dumps(block).encode()).hexdigest()
        return hash_operation
    
    def is_chain_valid(self):
        if len(self.chain) <= 1:
            return True  # Blockchain dengan satu atau tidak ada block dianggap valid

        prev_block = self.chain[0]
        now_index = 1  # Inisialisasi indeks dengan 1
        while now_index < len(self.chain):
            now_block = self.chain[now_index]

            # 1. cek apakah hash now block = prev hash 
            prev_hash = self.get_hash(prev_block)
            if prev_hash != now_block['prev_hash']:
                return False

            # 2. cek apakah proof of worknya true
            now_proof = now_block['proof']
            prev_proof = prev_block['proof']
            hash_operation = hashlib.sha256(str(now_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            prev_block = now_block
            now_index += 1  # Naikkan indeks

        return True
    
    #Simpan hash block didalam blocknya
    def create_block(self, proof, prev_hash, proof_of_work, data=None):
        block = {
            'id_block': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prev_hash': prev_hash,
            'proof_of_work': proof_of_work,
            'data': data  # Menambahkan data ke dalam blok
        }

        # Hitung hash blok dan simpan dalam block
        block['hash'] = self.get_hash(block)

        self.chain.append(block)
        return block


# 2. Web Aplikasi untuk Testing
app = Flask(__name__)

blockchain = Blockchain()

# buat endpoint 
@app.route("/get_chain", methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route("/mining", methods=['GET'])
def mining():
    prev_block = blockchain.get_last_block()
    # get prev proof
    prev_proof = prev_block['proof']
    proof, proof_of_work = blockchain.proof_of_work(prev_proof)
    # get prev hash
    prev_hash = blockchain.get_hash(prev_block)
    
    # Dapatkan panjang blockchain saat ini
    chain_length = len(blockchain.chain)
    
    # Buat data transaksi yang sesuai dengan urutan blockchain
    data_to_add = f"Transaksi {chain_length + 1}"
    
    # Create block dengan data yang telah dibuat
    created_block = blockchain.create_block(proof, prev_hash, proof_of_work, data=data_to_add)
    
    response = {
        'message': "Blockchain is successfully created",
        'created block': created_block
    }
    return jsonify(response), 200

# endpoint yang mengecek apakah chainnya valid
@app.route("/is_valid", methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid()
    if is_valid:
        response = {
            'message': "Blockchain is valid."
        }
        return jsonify(response), 200
    else:
        response = {
            'message': "Blockchain is not valid."
        }
        return jsonify(response), 400
    
@app.route("/ruined", methods=['GET'])
def ruin_chain():
    curr_block = blockchain.get_last_block()
    curr_block['prev_hash'] = curr_block['hash']
    response = {
        'message': "Blockchain has been ruined",
        'block': curr_block
    }
    return jsonify(response), 200
    
app.run()
