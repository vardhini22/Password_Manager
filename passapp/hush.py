import hashlib
def sha(text):
  sha3_hash = hashlib.sha3_256()
  sha3_hash.update(text.encode('utf-8'))
  hashed_string = sha3_hash.hexdigest()
  return hashed_string