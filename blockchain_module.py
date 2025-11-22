import hashlib
import time
import rsa
# انشاء المفاتيح من اجل التوقيع الرقمي 
public_key, private_key = rsa.newkeys(1024)
#class blocke  من اجل تحديد القالب الخاص بالبلوك و خصائصه من اجل استخدامه لاحقا بسهولة 
class Block:
    def __init__(self, transactions, index, previous_hash="0", block_version="1", difficulty=2): 
        #خصائص البلوك
        self.timestamp = time.time()
        self.index = index  #من اجل ترتيب البلوك 
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.block_version = block_version
        self.difficulty = difficulty
        self.nonce = 0
        self.merkle_root = self.compute_merkle_root() #method يتم حسابها لاحقا كما تعتبر خاصية
        self.hash = self.proof_of_work() #خاصية و ميتود يتم حسابها لاحقا 
# حساب الmerckelroot  نحتاجها لحساب هاش البلوك 
    def compute_merkle_root(self):
        hashes = [hashlib.sha256(str(tx).encode()).hexdigest() for tx in self.transactions]
        while len(hashes) > 1:
            new_hashes = []
            for i in range(0, len(hashes), 2):
                if i + 1 < len(hashes):
                    combined = hashes[i] + hashes[i+1]
                    new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
                else:
                    new_hashes.append(hashes[i])
            hashes = new_hashes
        return hashes[0] if hashes else "0"
# الميثود الخاصة باثبات العمل (يتم حساب الهاش مع ايجاد رقم ال...nonce )
    def proof_of_work(self):
        print(f"\nCalculating Proof of Work for block : {self.merkle_root}")
        block_hash = ""
        while not block_hash.startswith("0" * self.difficulty):
            block_string = f"{self.timestamp}{self.merkle_root}{self.previous_hash}{self.block_version}{self.nonce}"
            block_hash = hashlib.sha256(block_string.encode()).hexdigest()
            self.nonce += 1
        print(f"Block mined! Nonce: {self.nonce - 1}, Hash: {block_hash}")
        return block_hash

# كلاس من اجل انشاء البلوك شاين 
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()
# ميثود لانشاء اول بلوك 
    def create_genesis_block(self):
        genesis_tx = [{
            "sender": "0",
            "receiver": "Genesis",
            "amount": 0,
            "fee": 0,
            "signature": b"None"
        }]
        genesis_block = Block(
        index=0,
        transactions=genesis_tx,
        previous_hash="0"
    )
        self.chain.append(genesis_block)
# ميثود لاضافة بلوك جديد للسلسلة 
    def add_block(self, transactions):
        signed_transactions = []
        for tx in transactions:
            tx_string = f"{tx['sender']}{tx['receiver']}{tx['amount']}{tx['fee']}"
            signature = rsa.sign(tx_string.encode(), private_key, 'SHA-256')
            tx['signature'] = signature
            signed_transactions.append(tx)

        prev_hash = self.chain[-1].hash
        new_block = Block(
        index=len(self.chain),
        transactions=signed_transactions,
        previous_hash=prev_hash
    )
        self.chain.append(new_block)
      #من اجل التحقق من صحة البلوك 
    def validate_block(self, block, previous_block):
        # التحقق من الهاش السابق
        if block.previous_hash != previous_block.hash:
            return False

        # التحقق من الMerckel root 
        if block.compute_merkle_root() != block.merkle_root:
            return False

        # التحقق من خوارزمية التوافق pow
        if not block.hash.startswith("0" * block.difficulty):
            return False

        # التاكد من الهاش من خلال اعادة حسابه 
        block_string = f"{block.timestamp}{block.merkle_root}{block.previous_hash}{block.block_version}{block.nonce-1}"
        recomputed_hash = hashlib.sha256(block_string.encode()).hexdigest()

        if recomputed_hash != block.hash:
            return False

        # التحقق من التوقيع الرقمي 
        for tx in block.transactions:
            if tx["sender"] != "0":
                tx_string = f"{tx['sender']}{tx['receiver']}{tx['amount']}{tx['fee']}"
                try:
                    rsa.verify(tx_string.encode(), tx["signature"], public_key)
                except:
                    return False

        return True

    #التحقق من صحة البلوك شاين 
    def validate_chain(self):
        for i in range(1, len(self.chain)):
            if not self.validate_block(self.chain[i], self.chain[i-1]):
                print(f" Blockchain INVALID at block {i}")
                return False
        print(" Blockchain is VALID!")
        return True
#ميثود لعرض كل البلوكات و المعاملات 
    def display_chain(self):
        for i, block in enumerate(self.chain):
            print(f"\n--- Block {i} ---")
            print("Timestamp:", block.timestamp)
            print("Previous Hash:", block.previous_hash)
            print("Merkle Root:", block.merkle_root)
            print("Hash:", block.hash)
            print("Transactions:")
            for tx in block.transactions:
                print(f"  Sender: {tx['sender']}, Receiver: {tx['receiver']}, Amount: {tx['amount']}, Fee: {tx['fee']}")
                if tx['signature'] != b"None":
                    tx_string = f"{tx['sender']}{tx['receiver']}{tx['amount']}{tx['fee']}"
                    try:
                        rsa.verify(tx_string.encode(), tx['signature'], public_key)
                        print("    Signature: Valid")
                    except rsa.VerificationError:
                        print("    Signature: Invalid")
                else:
                    print("    Signature: None (Genesis)")



#  لتشغيل المحاكي الخاص بالبلوك شاين 
blockchain = Blockchain()

block_number = 1

while True:
    print(f"\nEnter 3 transactions for block {block_number}:")
    transactions = []

    for i in range(3):
        sender = input("Sender: ")
        receiver = input("Receiver: ")
        amount = float(input("Amount: "))
        fee = float(input("Fee: "))
        transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "fee": fee
        })

    blockchain.add_block(transactions)

    # لترك الحرية للمستخدم في حال اراد اضافة بلوك او لا 
    choice = input("\nDo you want to add another block? (y/n): ").lower() # لسؤال المستخدم 

    if choice != "y": # ادا اختار نعم فعندها يتم اصافة البلوك بعد تحديد المعاملات 
        print("\n\nBlockchain creation finished! Here is your full chain:\n")
        blockchain.display_chain()
        print("\nThank you for using the mini-blockchain simulator!") #ادا اختار لا  يتم اعطاء البلوك شاين شاملا 
        break

    block_number += 1 # من اجل وضع رقم ترتيب البلوك عند اضافته 
