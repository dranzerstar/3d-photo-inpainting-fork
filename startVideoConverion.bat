@echo off
rem mkdir vidconversiontemp

del ./READY
echo %1 >WORKING
 

%infile% =

cd C:\pipdir\3d-photo-inpainting-fork\

python main23.py --v %1 --r 25 --config argumentv.yml



ffmpeg -i "%~dpn1-conv.mp4" -i %1 -c copy -map 0:v -map 1:a "%~dpn1-convg.mp4"  

cd C:\pipdir\3d-photo-inpainting-fork\

copy "%~dpn1-convg.mp4"  C:\xampp\htdocs\dashboard\converted


del ./WORKING

echo a >READY
                                                                                                                                                                                                                                       
