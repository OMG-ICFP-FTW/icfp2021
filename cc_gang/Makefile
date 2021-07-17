all: steez forbidden

steez:
	g++ --std=gnu++14 -mavx -O3 -g3 `sdl2-config --libs --cflags` -o steez steez.cc -lSDL2 -lcurl -lpthread

forbidden:
	g++ --std=gnu++14 -march=native -fno-omit-frame-pointer -O3 -g3 -o forbidden forbidden.cc -lcurl -lpthread
