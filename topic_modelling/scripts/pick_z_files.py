from pathlib import Path
import random
import argparse
from glob import glob
from datetime import datetime
import os
import shutil

def latest_runsuite(Path_to_runs_dir):
    if Path_to_runs_dir.split('/')[-1]=='':
        Path_to_runs_dir=Path_to_runs_dir+'*'
    elif Path_to_runs_dir.split('/')[-1]=='Runs':
        Path_to_runs_dir=Path_to_runs_dir+'/*'
    else: 
        print('wrong path')
        return -1

    dir_paths=glob('/Users/liamtabibzadeh/Documents/jobb/PartiallyCollapsedLDA/Runs/*')
    times=[]
    for runsuite_path in dir_paths:
        time_in_datetime = datetime.strptime(runsuite_path.split('/')[-1][8:], '%Y-%m-%d--%H_%M_%S')
        times.append(time_in_datetime)

    right_runsuite=max(times).strftime('%Y-%m-%d--%H_%M_%S')
    for runsuite_path in dir_paths:
        if right_runsuite in runsuite_path:
            return runsuite_path
    print('wrong')
    return -1
        

def main(args):
    #make directory
    dir_tree=args.path_to_topic_model_dir.split('/')
    if dir_tree[-1]=='':
        z_files_dir = args.path_to_topic_model_dir + 'z_files/'
    elif dir_tree[-1]=='topic_modelling':
        z_files_dir = args.path_to_topic_model_dir + '/z_files/'
    else:
        print('bad path to topic modelling dir')
        return -1
    
    if os.path.exists(z_files_dir):
        shutil.rmtree(z_files_dir)
    os.makedirs(z_files_dir)

    runsuite_path=latest_runsuite(args.path_pclda_runs_dir)

    p = Path(runsuite_path)

    #find all z-files
    z_files = list(p.rglob('z_[0-9]*.csv'))
    #random sample of three files
    indices_sample=random.sample(range(1,len(z_files)), 3)
    #copy
    for index_sample in indices_sample:
        shutil.copyfile(z_files[index_sample], z_files_dir + z_files[index_sample].name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path_pclda_runs_dir", "-p1", type=str, default='/Users/liamtabibzadeh/Documents/jobb/PartiallyCollapsedLDA/Runs')
    parser.add_argument("--path_to_topic_model_dir", "-p2", type=str, default='/Users/liamtabibzadeh/Documents/jobb/dagens_nyheter/topic_modelling')    
    args = parser.parse_args()
    main(args)