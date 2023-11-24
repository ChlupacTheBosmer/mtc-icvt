#!/bin/bash
#PBS -N YOLOtrain
#PBS -l select=1:ncpus=1:ngpus=2:mem=10gb:scratch_local=1gb
#PBS -l walltime=2:00:00
#PBS -m ae
# The 4 lines above are options for scheduling system: job will run 1 hour at maximum, 1 machine with 4 processors +
# 4gb RAM memory + 10gb scratch memory are requested, email notification will be sent when the job aborts (a) or ends (e)

# DEFINE VARIABLES
# define a HOMEDIR variable: directory where the input files are taken from and where output will be copied to
HOMEDIR=/storage/brno2/home/$USER/
SING_IMAGE=$HOMEDIR/jobs/Ultralytics-8.0.199.sif

# append a line to a file "jobs_info.txt" containing the ID of the job, the hostname of node it is run on and the path to a scratch directory
# this information helps to find a scratch directory in case the job fails and you need to remove the scratch directory manually
echo "$PBS_JOBID is running on node `hostname -f` in a scratch directory $SCRATCHDIR" >> $HOMEDIR/jobs_info.txt,

cp -r  $HOMEDIR/jobs/clearml.conf $SCRATCHDIR/clearml.conf

# load modules here
# test if scratch directory is set
# if scratch directory is not set, issue error message and exit
test -n "$SCRATCHDIR" || { echo >&2 "Variable SCRATCHDIR is not set!"; exit 1; }

# move into scratch directory
cd $SCRATCHDIR

# Run calculations
#singularity exec -B $HOMEDIR:/mnt \
# $SING_IMAGE pip install clearml clearml-agent

#singularity exec -B $HOMEDIR:/mnt \
#$SING_IMAGE python $HOMEDIR/pycharm/mtc-icvt/metacentrum/test_script.py

singularity exec -B $HOMEDIR:/mnt \
$SING_IMAGE /bin/bash -c "pip install clearml; python '$HOMEDIR/pycharm/mtc-icvt/metacentrum/modules/mtc-train/train.py' --dataset '0709b8c1' --datasets_dir\
 '$HOMEDIR/datasets' --workdir '$HOMEDIR/' --project_name 'Test of MTC'"

#singularity exec -B $HOMEDIR:/mnt $SING_IMAGE $HOMEDIR/pycharm/mtc-icvt/metacentrum/run_in_image.sh
#
#singularity exec -B $HOMEDIR:/mnt \
#$SING_IMAGE "pip uninstall opencv && rm -rf  /usr/local/lib/python3.10/dist-packages/cv2 && apt update && apt install  libx11-6 && ls /mnt && pip install clearml clearml-agent && python $HOMEDIR/pycharm/mtc-icvt/metacentrum/modules/mtc-train/train.py --dataset '0709b8c1' --datasets_dir\
#  $HOMEDIR/datasets' --workdir '$HOMEDIR/' --project_name 'Test of MTC'"

#
#singularity exec -B $HOMEDIR:/mn
#t \
#$SING_IMAGE clearml-agent daemon --queue default

# Copy everything from scratch directory to $HOME/jobs
cp -r $SCRATCHDIR/* $HOMEDIR/jobs/
cp test_output.txt $HOMEDIR/ || { echo >&2 "Result file(s) copying failed (with a code $?) !!"; exit 4; }

clean_scratch