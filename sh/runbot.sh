#!/bin/sh

ROOT_PATH=/config/workspace/project

check=`ps -ef | grep homing | wc | awk '{print $1}'`

if [ $check -gt 1 ]; then
    echo "현재 전서구 봇이 실행 중 입니다."

else
    
    LOG_PATH=${ROOT_PATH}/logs/DoveNest/BOT

    echo "실행 코드가 있는 곳으로 이동 \n"
    cd ${ROOT_PATH}/DoveNest
    echo 현재 작업 디렉토리 입니다.
    pwd

    today=$(date "+%Y-%m-%d")
    yesterday=$(date -d "yesterday" "+%Y-%m-%d")

    mkdir -p $LOG_PATH/${yesterday}_logs
    mv $LOG_PATH/${yesterday}*.* $LOG_PATH/${yesterday}_logs
    zip -r $LOG_PATH/${yesterday}_logs.zip ${LOG_PATH}/${yesterday}_logs
    rm -rf ${LOG_PATH}/${yesterday}_logs

    echo "\n오늘 날짜 입니다." $today

    if [ -d $LOG_PATH ]; then
        echo "\n로그를 저장할 폴더가 이미 존재합니다."
        
        idx=$(ls -l $LOG_PATH | grep $today | grep ^- | wc -l)
        while [ ${#idx} -ne 3 ]; do
            idx="0"$idx
        done

    else
        mkdir -p $LOG_PATH
        echo "로그를 저장할 폴더가 생성되었습니다."
        idx="000"
    fi

    LOG_PATH=${LOG_PATH}/${today}_dovenest_bot_${idx}.log
    echo 이번에 생성할 로그 파일 경로 입니다. ${LOG_PATH}

    echo "\n전서구 봇을 실행합니다."
    nohup python $ROOT_PATH/DoveNest/homing_pigeon.py > $LOG_PATH &
fi