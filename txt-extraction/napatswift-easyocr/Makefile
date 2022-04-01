main_built := ./built/main

main:
	g++ -O3 -std=c++11 main.cpp `pkg-config --cflags --libs tesseract opencv4 Magick++` -o $(main_built)
	$(main_built)

cvt_pdf:
	rm ./input/2022_3-5/**.jpg
	convert -verbose -density 150 ./input/pdf/2022_3-5.pdf\[131-220\] -quality 100 -sharpen 0x1.0 ./input/2022_3-5/page-%03d.jpg
clean:
	rm ./output/2022-3_3-2/**.jpg
	rm $(main_built)

