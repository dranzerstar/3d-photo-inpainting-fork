mkdir vidconversiontemp
 
python main23.py --v %1  --config argumentv.yml 
rem ffmpeg -i %1 -filter_complex "scale=1920:1080" -r 30 .\vidconversiontemp\tempfilename%%03d.jpg

rem python main2.py --config argumentv.yml


rem ffmpeg -i 5d428d0529166e04fd2b222c.mp4 -r 30 -f image2 -start_number 1 -r 30 -i .\depthframe\tempfilename%%03d_disp.jpg -filter_complex "[1:v]scale=1920:1080[b],[0:v][b]hstack,scale=3840:2160,setsar=1/1" -pix_fmt yuv420p -r 24 -crf 16 out.mp4
                                                                                                                                                                                                                                       
rem del /q vidconversiontemp\*
rem del /q depthframe\*
rem del /q vidconversiondepth\*

