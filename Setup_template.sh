export DATA_dir=$PWD/data/TestResults
export GUI_dir=$PWD

export UsePowerSupplyLib=false

if [ ! -d $PH2ACF_BASE_DIR ]; then
    echo "Error: PH2ACF_BASE_DIR not found!"
fi;

if [ ! -d $DATA_dir ]; then
    echo "DATA_dir not found!  Making it now!"
    mkdir -p -m777 $DATA_dir
fi;

if [ ! -d $PH2ACF_BASE_DIR/test ]; then 
    echo "Test directory not found!  Making it now!"
    mkdir -p -m777 $PH2ACF_BASE_DIR/test;
fi;

if [ ! -d $DATA_dir ]; then
    echo "Failed to create TestResults folder under DATA_dir, please check"
fi;

if [ ! -d $PH2ACF_BASE_DIR/test ]; then
    echo "Failed to create test folder under PH2ACF_BASE_DIR, please check"
fi;



if [ "$UsePowerSupplyLib" = true ]
then
    export PowerSupplyArea=$PWD/power_supply
else
    unset PowerSupplyArea
fi
export PYTHONPATH=${PYTHONPATH}:${GUI_dir}

#export DATA_dir=/Users/czkaiweb/Research/data/
chmod 755 $PWD/Gui/GUIutils/*.sh

cd $PH2ACF_BASE_DIR
source setup.sh
export Ph2_ACF_VERSION=$(git describe --tags --abbrev=0)

if [ "$UsePowerSupplyLib" = true ]
then
    cd $PowerSupplyArea
    source setup.sh
fi
cd $GUI_dir
