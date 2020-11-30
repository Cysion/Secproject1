import json
import os
import argparse

def from_json(tree="lang", jsonfp="conf/lang.json") -> None:
    """converts a file to a csv tree from a json file
    tree = location of the tree
    jsonfp = location of the json file"""
    if not tree or not jsonfp:
        tree, jsonfp="lang","conf/lang.json"
    lang_dict = {}
    with open(jsonfp) as inf:
        lang_dict = json.load(inf)
    to_tree(lang_dict, tree)
    return



def to_tree(jasoon: dict, cwd: str) -> None:
    """recursively crawls json file and unpacks it to a csv tree
    jasoon = dict to unpack OR synthpop band from malmö featuring lead singer tinbuktu
    cwd = root dir to unpack to"""
    csvify = lambda key, stuff: ",".join([f'"{i}"' for i in tuple([key] + [stuff] if type(stuff) == str else [key] + stuff)])
    with open(os.path.join(cwd, os.path.join(os.path.split(cwd)[-1] + ".csv")), "w") as outf:
        for key in jasoon:
            if type(jasoon[key]) == dict:
                try:
                    os.mkdir(os.path.join(cwd, key))
                except FileExistsError:
                    pass
                to_tree(jasoon[key], os.path.join(cwd, key))
            else:
                csvified = csvify(key, jasoon[key])
                outf.write(csvified + "\n")
    return


def from_tree(tree="lang", jsonfp="conf/lang.out.json") -> None:
    """converts a file to a csv tree from a json file
    tree = location of the tree
    jsonfp = location of the json file"""
    if not tree or not jsonfp:
        tree, jsonfp="lang","conf/lang.out.json"
    dicc = to_json(tree)
    with open(jsonfp, "w") as outf:
        json.dump(dicc, outf, indent=4)
    return
    
    
def to_json(cwd: str) -> dict:
    """recursively crawls a csv tree and packs it into a pythonic dictionary.
    cwd = root to csv dir to pack"""
    dicc = {}
    for thing in os.listdir(cwd):
        if os.path.isdir(os.path.join(cwd, thing)):
            dicc[thing] = to_json(os.path.join(cwd, thing))
        else:
            with open(os.path.join(cwd, thing)) as inf:
                for line in inf.readlines():
                    line.rstrip()
                    line = line[1:-2].split('","')
                    dicc[line[0]] = []
                    try:
                        dicc[line[0]] = line[1] if len(line) <= 2 else line[1:]
                    except IndexError:
                        pass
    return dicc


def test_sim(dict1, dict2, revved=0):
    """tests if dict1 and dict2 are identical"""
    assert type(dict1) == dict
    assert type(dict2) == dict
    for key in dict1:
        if type(dict2[key]) == dict:
            test_sim(dict2[key], dict1[key])
        assert dict1[key] == dict2[key]
    if not revved:
        test_sim(dict2, dict1, 1)
    return 1


def main():
    to_opt = {
        "json":from_tree,
        "tree":from_json
    }
    parsy = argparse.ArgumentParser("A tool to convert a lang json to csv files, and back")
    parsy.add_argument("-j", "--json", metavar='"json file"', help="path to the chosen json file. defaults to ./lang.out.json")
    parsy.add_argument("-t", "--tree", metavar='"csv tree"', help="path to the chosen csv tree. defaults to ./lang")
    parsy.add_argument("-c", "--convert-to", choices=to_opt.keys(), dest="convert", required=True, help="convman will convert lang json to csv tree or csv tree to lang json")
    args = parsy.parse_args()
    try:
        to_opt[args.convert](jsonfp = args.json, tree = args.tree)
    except FileNotFoundError as e:
        print(e)
    except FileExistsError as e:
        print(e)

if __name__ == "__main__":
    main()
    