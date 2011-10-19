all:
	python setup.py build
	#find build -name align.so | xargs -J % cp % PI
	find build -name align.so -exec cp {}  PI/ \;

install:
	python setup.py install

clean:
	find . -name "*.pyc" | xargs rm -f
	rm -f PI/align.c
	rm -rf build

