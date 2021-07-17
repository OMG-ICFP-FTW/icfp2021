all:
	g++ --std=gnu++14 -mavx -O3 -g3 `sdl2-config --libs --cflags` -o steez steez.cc -lSDL2 -lcurl -lpthread
	g++ --std=gnu++14 -mavx -fno-omit-frame-pointer -O3 -g3 `sdl2-config --libs --cflags` -o forbidden forbidden.cc -lSDL2 -lcurl -lpthread
