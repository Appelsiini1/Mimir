with open("inst.txt", "r", encoding='utf-8') as file:
    data = file.read()
    #print(data)
    new_data = data.replace("\\", "\\\\").replace("\\n", "\\\n").replace('"', "'").replace("\t", "\\t")
    new_data = new_data.replace("\n", "\\n")
with open("res.txt", "w", encoding='utf-8') as new_file:
    new_file.write(new_data)

# with open("poc_L01T1.txt", "r", encoding='utf-8') as newnew_file:
#     data = newnew_file.read()
#     print(data)
#     print("###########")
#     print(data.replace("\\n", "\n").replace("\\\n", "\\n").replace("\\t", "\t").replace("'", '"'))
