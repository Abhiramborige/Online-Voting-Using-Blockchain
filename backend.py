
import hashlib
from time import time
from urllib.parse import urlparse
import requests
import json
from uuid import uuid4

class Blockchain:
    
    # Initialization of PARAMETERS
    def __init__(self):
        # one for storing transactions and 
        # the other for storing chain of blocks
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        # Creation of genesis block
        self.new_block(previous_hash=1, proof=100)
        
    def register_node(self, address):
        # Adds new NODE to the LIST OF NODES
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def valid_chain(self, chain):
        # Determine whether given BLOCKCHAIN is valid
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check whether HASH of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof'],self.hash(last_block)):
                return False
        last_block = block
        current_index += 1
        return True
    
    def resolve_conflicts(self):
        # CONSENSUS algorithm
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            # node stands for different centers of voting i.e, Polling centers
            # Polling centers are nothing but voter's vote input system
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, proof, previous_hash=None):
        # Creates NEW BLOCK in chain
        # uuid is the Universal Unique Identifier, generated randomly
        # which is a session key, vary from each session of poll. 
        # This is generated just before appending vote block into chain
        node_identifier = str(uuid4()).replace('-', '')
        block = {
            'index': len(self.chain) + 1,
            # This method returns the time as a floating point number 
            # expressed in seconds since the epoch January 1, 1970
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'session_key': node_identifier,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            }
        self.current_transactions = []
        self.chain.append(block)
        return block
    
    def new_transaction(self, Party_A , Party_B):
        self.current_transactions.append({
            # Part_A is the nominee participating in the elections
            # Party_B is the voter who votes
            'Party_A': Party_A,
            'Party_B': Party_B,
            'Votes': 1
            })
        return self.last_block['index'] + 1
    
    @property
    def last_block(self):
        return self.chain[-1]
    
    @staticmethod
    def hash(block):
        # SHA-256, HASH of a Block
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        # PROOF OF WORK
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
