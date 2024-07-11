from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os, sys
import operator
import string
import re
from collections import Counter
from flask import send_file


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
 
# Define allowed files
ALLOWED_EXTENSIONS = {'txt'}
 
app = Flask(__name__)
 
# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

words = []

@app.route('/',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      data = request.form['word']
      temp_list = []
      temp_list.append(data)
      file_statistics()
      result = spell_corrector_wrapper(temp_list)
      return render_template("result.html", result = result)
   else:
      return render_template("result.html")

@app.route('/download',methods = ['GET'])
def downloadFile ():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "result.txt"
    return send_file(path, as_attachment=True)

@app.route('/file_upload',methods = ['POST'])
def file_upload():
   if request.method == 'POST':
        file = request.files['customFile']
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        data = get_data(file_path)
        file_statistics()
        data = spell_corrector_wrapper(data)
        create_result_file(data)
        return render_template('result.html', content=data)
   else:
      return render_template("result.html")

def create_result_file(data):
    # Using open() function
    file_path = "./result.txt"
    
    # Open the file in write mode
    with open(file_path, 'w') as file:
        # Write content to the file
        for line in data:
            data = ("(%s , %s)\n")%(line[0],line[1])
            file.writelines(data)
        
    print(f"File '{file_path}' created successfully.")

def get_data(file):
   temp_list = []
   file = open(file, 'r')
   Lines = file.readlines()
   for line in Lines:
      temp_list.append(line.strip())
   return temp_list

def file_statistics():
   global words
   words = []
   with open("internet_archive_scifi_v3.txt", "r") as f:
         lines = f.readlines()
         for line in lines:
            words += re.findall(r'\w+', line.lower())
         print(words[0:10])
         print(f'Total words in text file is {len(words)}')
   return words
   

def spell_corrector_wrapper(string_list):
    #print("in_word : " ,in_word, " out_word : " , ret)
    out_list = []
    for i in string_list:
        ret = spell_corrector(i)
        out_list.append((i , ret))
    return out_list

def spell_corrector(word):
    ret_str = ""
    vocabulary = set(words)
    print(f"There are {len(vocabulary)} in vocabulary")
    word_count=Counter(words)
    #word_count['a']
    total_words=sum(word_count.values())
    total_words
    word_probabilities = {word: word_count[word] / total_words for word in word_count.keys()}
    #word_probabilities['a']
    returned_prob = correct_spelling(word, vocabulary, word_probabilities)
    if(returned_prob == "COR"):
        ret_str = "ALREADY CORRECT"
        #print("ALREADY CORRECT WORD")
    else:
        size = len(returned_prob)
        if(size == 0):
            ret_str = "OOV WORD"
            #print("OOV" )
        else:
            sorted_list=sorted(returned_prob, key = operator.itemgetter(1))
            #print("highest prob",sorted_list[size-1] )
            ret_str = sorted_list[size-1][0]
    return ret_str
            
def correct_spelling(word, vocabulary, word_probabilities):
    if word in vocabulary:
        #print(f"{word} is already correctly spelt")
        return "COR"

    suggestions = generate_combinations(word) or [word]
    best_guesses = [w for w in suggestions if w in vocabulary]
    return [(w, word_probabilities[w]) for w in best_guesses]

def generate_combinations(word):
    letters = string.ascii_lowercase
    splitword = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deleteword = [l + r[1:] for l,r in splitword if r]
    swapword = [l + r[1] + r[0] + r[2:] for l, r in splitword if len(r)>1]
    replaceword = [l + c + r[1:] for l, r in splitword if r for c in letters]
    insertword = [l + c + r for l, r in splitword for c in letters] 

    return set(deleteword + swapword + replaceword + insertword)

def swap_word(word):
    return [l + r[1] + r[0] + r[2:] for l, r in split_word(word) if len(r)>1]

def replace_word(word):
    letters = string.ascii_lowercase
    return [l + c + r[1:] for l, r in split_word(word) if r for c in letters]

def split_word(word):
    return [(word[:i], word[i:]) for i in range(len(word) + 1)]

def delete_word(word):
    return [l + r[1:] for l,r in split_word(word) if r]

if __name__ == '__main__':
   app.run(debug = True)