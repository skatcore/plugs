#include <time.h>
#include <stdint.h>
//#include <bcm2835.h>

// Access from ARM Running Linux

#define BCM2708_PERI_BASE        0x20000000
#define GPIO_BASE                (BCM2708_PERI_BASE + 0x200000) /* GPIO controller */


#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

#define PAGE_SIZE (4*1024)
#define BLOCK_SIZE (4*1024)

int  mem_fd;
void *gpio_map;

// I/O access
volatile unsigned *gpio;


// GPIO setup macros. Always use INP_GPIO(x) before using OUT_GPIO(x) or SET_GPIO_ALT(x,y)
#define INP_GPIO(g) *(gpio+((g)/10)) &= ~(7<<(((g)%10)*3))
#define OUT_GPIO(g) *(gpio+((g)/10)) |=  (1<<(((g)%10)*3))
#define SET_GPIO_ALT(g,a) *(gpio+(((g)/10))) |= (((a)<=3?(a)+4:(a)==4?3:2)<<(((g)%10)*3))

#define GPIO_SET *(gpio+7)  // sets   bits which are 1 ignores bits which are 0
#define GPIO_CLR *(gpio+10) // clears bits which are 1 ignores bits which are 0

void setup_io();

//
// Set up a memory regions to access GPIO
//
void setup_io()
{
   /* open /dev/mem */
   if ((mem_fd = open("/dev/mem", O_RDWR|O_SYNC) ) < 0) {
      printf("can't open /dev/mem \n");
      exit(-1);
   }

   /* mmap GPIO */
   gpio_map = mmap(
      NULL,             //Any adddress in our space will do
      BLOCK_SIZE,       //Map length
      PROT_READ|PROT_WRITE,// Enable reading & writting to mapped memory
      MAP_SHARED,       //Shared with other processes
      mem_fd,           //File to map
      GPIO_BASE         //Offset to GPIO peripheral
   );

   close(mem_fd); //No need to keep mem_fd open after mmap

   if (gpio_map == MAP_FAILED) {
      printf("mmap error %d\n", (int)gpio_map);//errno also set!
      exit(-1);
   }

   // Always use volatile pointer!
   gpio = (volatile unsigned *)gpio_map;
   printf("SETUP FINISHED");
} // setup_io


/* this will register an contructor that calls the setup_io() when the app starts */
static void con() __attribute__((constructor));

void con() {
    setup_io();
}



/* use this to send power to a pin */
void set_pin(int pin) {
	GPIO_SET = 1<<pin;
}

/* use this to set no power to a pin */
void clr_pin(int pin) {
	GPIO_CLR = 1<<pin;
}

void tx_value(uint8_t value){
	set_pin(17);
	nanosleep((const struct timespec[]){{0,370000L}}, NULL);
	clr_pin(17);
	nanosleep((const struct timespec[]){{0,1110000L}}, NULL);
	
	
	if(value){
		set_pin(17);
		nanosleep((const struct timespec[]){{0,370000L}}, NULL);
		clr_pin(17);
		nanosleep((const struct timespec[]){{0,1110000L}}, NULL);
	}else{
		set_pin(17);
		nanosleep((const struct timespec[]){{0,1110000L}}, NULL);
		clr_pin(17);
		nanosleep((const struct timespec[]){{0,370000L}}, NULL);
	}
}


/*
	house code hc as dec value
	switch code sc as dec value
*/
void send_pc(uint8_t hc, uint8_t sc){
	tx_value((hc>>4)&0x01);
	tx_value((hc>>3)&0x01);
	tx_value((hc>>2)&0x01);
	tx_value((hc>>1)&0x01);
	tx_value((hc)&0x01);
	tx_value((sc>>4)&0x01);
	tx_value((sc>>3)&0x01);
	tx_value((sc>>2)&0x01);
	tx_value((sc>>1)&0x01);
	tx_value((sc)&0x01);
}

/*
	status 0: off
	status 1: on
	
*/
void send_status(uint8_t status){
	tx_value(status);
	tx_value(!status);
}

void send_sync(){
	set_pin(17);
	nanosleep((const struct timespec[]){{0,370000L}}, NULL);
	clr_pin(17);
	nanosleep((const struct timespec[]){{0,1110000L}}, NULL);
	nanosleep((const struct timespec[]){{0,10360000L}}, NULL);
}

int main(int argc, char** argv)
{
    // this is called after the constructor!
 
    // you must run this as root!!!
    
	if(argc != 4){
		printf("\nUsage: <houseCode>,<switchCode>,<status> \n");
		return -1;
	}
	
	uint8_t hc = atoi(argv[1]);
	uint8_t sc = atoi(argv[2]);
	uint8_t status = atoi(argv[3]);
		
    INP_GPIO(17); // must use INP_GPIO before we can use OUT_GPIO
    OUT_GPIO(17);
    
	//for(uint8_t i=0;i<4;i++){
		send_pc(hc,sc);
		send_status(status);
		send_sync();
	//}
	printf("Transmission finished.\n");
}
