CC = g++
CFLAGS = -g -Wall
INCLUDES = -I/usr/local/opt/openssl/include/
LFLAGS = -L/usr/local/opt/openssl/lib
LIBS = -lssl -lcrypto 

SRCS = signature.cpp ascendex_util.cpp

OBJS = $(SRCS:.cpp=.o)

MAIN = signature

# TARGET= main

.PHONY: depend clean

all: 	${MAIN}
		@echo  Simple compiler named signature has been compiled

${MAIN}: $(OBJS)
		$(CC) $(CFLAGS) $(INCLUDES) -o $(MAIN) $(OBJS) $(LFLAGS) $(LIBS)
	
.cpp.o:
		$(CC) $(CFLAGS) $(INCLUDES) -c $<  -o $@

clean:
	${RM} main *.o *~

depend: $(SRCS)
	makedepend $(INCLUDES) $^