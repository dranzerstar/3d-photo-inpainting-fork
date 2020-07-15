@echo off
rem mkdir vidconversiontemp

 
python main23.py --v %1 --r 25 --config argumentv.yml

ffmpeg -i "%~dpn1-conv.mp4" -i %1 -c copy -map 0:v -map 1:a "%~dpn1-convg.mp4"  

                                                                                                                                                                                                                                       
rem del /q vidconversiontemp\*
rem del /q depthframe\*
rem del /q vidconversiondepth\*

