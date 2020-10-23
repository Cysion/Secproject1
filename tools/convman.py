import json

def from_json(infp="conf/lang.json", outfp="icantread.txt"):
    lang_dict = {}
    with open(infp) as inf, open(outfp, "w") as outf:
        lang_dict = json.load(inf)
        formatted = format_underlings(format_from_dict=lang_dict)
        print(formatted)
        outf.write(formatted)
    
def format_underlings(format_to_str="", format_from_dict={}):
    for key in format_from_dict:
        if type(format_from_dict[key]) == dict:
            format_to_str += format_underlings(format_to_str=format_to_str, format_from_dict=format_from_dict[key])
        elif type(format_from_dict[key]) == list:
            format_to_str += " | ".join(format_from_dict[key]) + "\n"
        elif type(format_from_dict[key]) == str:
            format_to_str += format_from_dict[key] + "\n"
        format_to_str += "\n"
    return format_to_str

if __name__ == "__main__":
    from_json()