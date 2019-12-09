/* http://l3net.wordpress.com/2012/12/09/a-simple-telnet-client/ */
// Considerably modified bu Nick Glazzard, 2019.

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <arpa/inet.h>
#include <termios.h>
#include <fcntl.h>
#include <stdarg.h>
#include <time.h>

// Defines
 
#define DO 0xfd
#define WONT 0xfc
#define WILL 0xfb
#define DONT 0xfe
#define CMD 0xff
#define CMD_ECHO 1
#define CMD_WINDOW_SIZE 3
#define BUFLEN 20

// Globals

static struct termios tin;            ///< Saved terminal characteristics on entry.
static FILE* flog = NULL;             ///< Log file.
static int send_crlf_at_newline = 0;  ///< Send LF to host after sending CR.
static int send_cr_after_lf = 0;      ///< Send CR to host after sending LF. Useless, probably.
static int show_lf_after_newline = 0; ///< Send LF to terminal after CR from terminal.
static int bytes_in=0;                ///< Bytes received from host.
static int bytes_out=0;               ///< Bytes sent to host.
static char* asciimap[] =             ///< ASCII byte values to string for log file.
  {
    "NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL",
    "BS",  "TAB", "LF",  "VT",  "FF",  "CR",  "SO",  "SI",
    "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
    "CAN", "EM",  "SUB", "ESC", "FS",  "GS",  "RS",  "US",
    " SP", "!",   "\"",  "#",   "$",   "%",   "&",   "'",
    "(",   ")",   "*",   "+",   ",",   "-",   ".",   "/",
    "0",   "1",   "2",   "3",   "4",   "5",   "6",   "7",
    "8",   "9",   ":",   ";",   "<",   "=",   ">",   "?",
    "@",   "A",   "B",   "C",   "D",   "E",   "F",   "G",
    "H",   "I",   "J",   "K",   "L",   "M",   "N",   "O",
    "P",   "Q",   "R",   "S",   "T",   "U",   "V",   "W",
    "X",   "Y",   "Z",   "[",   "\\",  "]",   "^",   "_",
    "`",   "a",   "b",   "c",   "d",   "e",   "f",   "g",
    "h",   "i",   "j",   "k",   "l",   "m",   "n",   "o",
    "p",   "q",   "r",   "s",   "t",   "u",   "v",   "w",
    "x",   "y",   "z",   "{",   "|",   "}",   "~",   "DEL",

    "8/NUL", "8/SOH", "8/STX", "8/ETX", "8/EOT", "8/ENQ", "8/ACK", "8/BEL",
    "8/BS",  "8/TAB", "8/LF",  "8/VT",  "8/FF",  "8/CR",  "8/SO",  "8/SI",
    "8/DLE", "8/DC1", "8/DC2", "8/DC3", "8/DC4", "8/NAK", "8/SYN", "8/ETB",
    "8/CAN", "8/EM",  "8/SUB", "8/ESC", "8/FS",  "8/GS",  "8/RS",  "8/US",
    " 8/SP", "8/!",   "8/\"",  "8/#",   "8/$",   "8/%",   "8/&",   "8/'",
    "8/(",   "8/)",   "8/*",   "8/+",   "8/,",   "8/-",   "8/.",   "8//",
    "8/0",   "8/1",   "8/2",   "8/3",   "8/4",   "8/5",   "8/6",   "8/7",
    "8/8",   "8/9",   "8/:",   "8/;",   "8/<",   "8/=",   "8/>",   "8/?",
    "8/@",   "8/A",   "8/B",   "8/C",   "8/D",   "8/E",   "8/F",   "8/G",
    "8/H",   "8/I",   "8/J",   "8/K",   "8/L",   "8/M",   "8/N",   "8/O",
    "8/P",   "8/Q",   "8/R",   "8/S",   "8/T",   "8/U",   "8/V",   "8/W",
    "8/X",   "8/Y",   "8/Z",   "8/[",   "8/\\",  "8/]",   "8/^",   "8/_",
    "8/`",   "8/a",   "8/b",   "8/c",   "8/d",   "8/e",   "8/f",   "8/g",
    "8/h",   "8/i",   "8/j",   "8/k",   "8/l",   "8/m",   "8/n",   "8/o",
    "8/p",   "8/q",   "8/r",   "8/s",   "8/t",   "8/u",   "8/v",   "8/w",
    "8/x",   "8/y",   "8/z",   "8/{",   "8/|",   "8/}",   "8/~",   "8/DEL"
  };

void logit( const char* fmt, ... )
//--------------------------------
/// @brief Conditionally write to a log file.
/// @param fmt Format string.
/// @param ... List of arguments for fmt.
{
  va_list args;
  if( flog != NULL ){
    va_start(args, fmt);
    vfprintf(flog, fmt, args);
    va_end(args);
    fflush(flog);
  }
}

void negotiate(int sock, unsigned char *buf, int len)
//---------------------------------------------------
/// @brief Handle telnet property negotiation with the host.
///
/// More or different things might be needed here for some host OSes.
/// DtCyber NPU simulation does no negotiation, so this isn't used there.
///
/// @param sock Socket file descriptor.
/// @param buf Buffer containing bytes of telnet CMD message from host.
/// @param len Number of bytes in buf.
{
  int i;
  logit( "INFO: negotiate() entered.\n" );

  // Handle window size request. Inform host 80 x 24.
  if (buf[1] == DO && buf[2] == CMD_WINDOW_SIZE) {
    logit( "... DO CMD_WINDOW_SIZE received.\n" );
    unsigned char tmp1[10] = {255, 251, 31};
    if (send(sock, tmp1, 3 , 0) < 0){
      perror("ERROR: Could not send() (negotiate case 1).");
      logit("ERROR: send() failed (negotiate case 1).\n");
      exit(1);
    }
    logit( "... sent: 255, 251, 31\n" );

    unsigned char tmp2[10] = {255, 250, 31, 0, 80, 0, 24, 255, 240};
    if (send(sock, tmp2, 9, 0) < 0){
      perror("ERROR: Could not send() (negotiate case 2).");
      logit("ERROR: send() failed (negotiate case 2).\n");
      exit(1);
    }
    logit( "... sent: 255, 250, 31, 0, 80, 0, 24, 255, 240\n" );
    logit( "... returning from negotiate()\n" );
    return;
  }

  // All other items...
  logit( "... %d characters in CMD buffer.\n", len );
  for (i = 0; i < len; i++) {

    // Host says DO, reply WONT.
    if (buf[i] == DO){
      buf[i] = WONT;
      logit( "... %d: DO --> WONT\n", i );
    }

    // Host says WILL, reply DO.
    else if (buf[i] == WILL){
      buf[i] = DO;
      logit( "... %d: WILL --> DO\n", i );
    }
  }
 
  if( send(sock, buf, len, 0) < 0 ){
    perror("ERROR: Could not send() (negotiate case 3).");
    logit("ERROR: send() failed (negotiate case 3).\n");
    exit(1);
  }
  logit( "... returning from negotiate() after sending %d chars to host.\n", len );
}
  
static void terminal_set( void )
//------------------------------
/// @brief Set terminal to raw mode.
{
  // Save current terminal configuration
  tcgetattr(STDIN_FILENO, &tin);

  // Make terminal raw.
  static struct termios tlocal;
  memcpy(&tlocal, &tin, sizeof(tin));
  cfmakeraw(&tlocal);
  tcsetattr(STDIN_FILENO,TCSANOW,&tlocal);
  logit("Terminal set to RAW.\n");
}
 
static void terminal_reset( void )
//--------------------------------
/// @brief Restore terminal's previous configuration. Called on exit.
{
  tcsetattr(STDIN_FILENO,TCSANOW,&tin);
  logit("Terminal reset.\n");
}

static int send_buf( int sock, unsigned char* buf, int n_send )
//-------------------------------------------------------------
/// @brief Send a buffer of bytes to the host.
/// @param sock Socket file descriptor.
/// @param buf Buffer containing bytes to send.
/// @param n_send Number of bytes to send.
/// @return 0 if OK, 1 if send() failed.
{
  int oc;

  // Record if it is a newline (LF) character (from return key usually).
  int is_newline = (buf[0] == '\n');

  // Apply any character transformations here.
  // \r -> CR LF.
  if( send_crlf_at_newline && (buf[n_send-1] == '\r') ){
    buf[n_send++] = '\n';
  }

  // \r -> LF CR.
  if( send_cr_after_lf && (buf[n_send-1] == '\r') ){
    buf[n_send++] = '\n';
  }
            
  // Send characters to host.
  if( send(sock, buf, n_send, 0 ) < 0){
    perror("ERROR Failed to send().");
    logit("ERROR: Failed to send(), %d characters.\n",n_send);
    return 1;
  }
  for( oc=0; oc<n_send; oc++ ){
    logit( "O                   %08d %02x %s\n", bytes_out, buf[oc], asciimap[buf[oc]] );
    ++bytes_out;
  }
      
  // If newline received from terminal emulator, send LF to terminal emulator.
  if( show_lf_after_newline && is_newline ){
    putchar('\r');
  }
  
  return 0;
}
 
int main(int argc , char *argv[])
//-------------------------------
/// @brief Implement a minimal but useful telnet client.
/// @param argc Command line argument count.
/// @param argv Command line word string argument pointers.
/// @return 0 if OK, else condition code.
{
  int sock;
  struct sockaddr_in server;
  unsigned char buf[BUFLEN + 1];
  int len;
  int ilist;
  int port;
  int ia;
  ssize_t n_send = 0;

  printf( "\nCTELNET: Minimal telnet client V0.1.\n" );
    
  // Parse command line.
  if( argc < 3 ){
    printf("ERROR: Usage: %s address port [--crlf --cr_after_lf --lfafternl --log]\n", argv[0]);
    logit("ERROR: Usage.\n", argv[0]);
    return 1;
  }
  port = atoi(argv[2]);

  for( ia=3; ia<argc; ia++ ){
    if( !strcmp( argv[ia], "--crlf" ) ){
      send_crlf_at_newline = 1;
      printf("INFO: --crlf is set.\n");
    }
    else if( !strcmp( argv[ia], "--cr_after_lf" ) ){
      send_cr_after_lf = 0;
      printf("INFO: --cr_after_lf is set.\n");
    }
    else if( !strcmp( argv[ia], "--lfafternl" ) ){
      show_lf_after_newline = 1;
      printf("INFO: --lfafternl is set.\n");
    }
    else if( !strcmp( argv[ia], "--log" ) ){
      char* homedir = getenv("HOME");
      if( homedir != NULL ){
        time_t now = time(0);
        char fullname[1024];
        snprintf(fullname,1023,"%s/ctelnet_log_%ld.txt",homedir,now);
        flog = fopen(fullname,"w");
        printf("INFO: --log to %s is set.\n",fullname);
      }
      if( flog == NULL ){
        fprintf(stderr, "ERROR: Cannot create log file.\n");
        return 1;
      }
    }
    else{
      fprintf( stderr, "WARNING: Unknown option: %s (ignored)\n", argv[ia]);
    }
  }
 
  // Create socket.
  sock = socket(AF_INET , SOCK_STREAM , 0);
  if (sock == -1) {
    perror("ERROR: Could not create socket.");
    logit("ERROR: Could not create socket.");
    return 1;
  }
 
  server.sin_addr.s_addr = inet_addr(argv[1]);
  server.sin_family = AF_INET;
  server.sin_port = htons(port);
 
  // Connect to host.
  if (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0) {
    perror("ERROR: Could not connect().");
    logit("ERROR: Failed to connect().\n");
    return 1;
  }
  puts("INFO: Connected ...\n");
  logit("INFO: Connected ...\n");
 
  // Set terminal to raw mode.
  terminal_set();
  atexit(terminal_reset);
     
  struct timeval ts;
  ts.tv_sec = 1; // 1 second
  ts.tv_usec = 0;

  // Loop forever ...
  while (1) {
      
    // Setup select()
    fd_set fds;
    FD_ZERO(&fds);
    if (sock != 0)
      FD_SET(sock, &fds);
    FD_SET(0, &fds);
 
    // Wait for data from either host or terminal emulator.
    int nready = select(sock + 1, &fds, (fd_set *) 0, (fd_set *) 0, &ts);
    if (nready < 0) {
      perror("ERROR: Could not select().");
      logit("Failed to select().\n");
      return 1;
    }

    // Nothing yet, wait 1 second.
    else if (nready == 0) {
      ts.tv_sec = 1;
      ts.tv_usec = 0;
    }

    // From host:
    else if (sock != 0 && FD_ISSET(sock, &fds)) {
          
      // Read a single byte.
      int rv;
      if ((rv = recv(sock , buf , 1 , 0)) < 0){
        perror("ERROR: Could not recv().");
        logit("ERROR: recv() failed (case 1).\n");
        return 1;
      }
      else if (rv == 0) {
        printf("INFO: Connection closed by the remote end\n\r");
        logit("INFO: Connection closed by the remote end (case 1)\n");
        return 0;
      }

      for( ilist=0; ilist<rv; ilist++ ){
        logit( "I %08d %02x %s\n", bytes_in, buf[ilist], asciimap[buf[ilist]] );
        ++bytes_in;
      }

      // If this is a telnet CMD, process it. 
      if (buf[0] == CMD) {
        
        // Read 2 more bytes
        len = recv(sock , buf + 1 , 2 , 0);
        if (len < 0){
          perror("ERROR: Could not recv() from socket.");
          logit("ERROR: recv() from socket failed (case 2)\n");
          return 1;
        }
        else if (len == 0) {
          printf("INFO: Connection closed by the remote end\n\r");
          logit("INFO: Connection closed by the remote end (case 2)\n");
          return 0;
        }

        // Handle telnet property negotiation with host.
        negotiate(sock, buf, 3);
      }

      // Send received data to the terminal emulator.
      else{
        len = 1;
        buf[len] = '\0';
        printf("%s", buf);
        fflush(stdout);
      }
    }

    // From terminal emulator:
    else if (FD_ISSET(0, &fds)) {

      // Read all available bytes from the terminal emulator.
      n_send = read(fileno(stdin), buf, BUFLEN);
      if( n_send < 0 ){
        perror("ERROR: Could not read() from stdin (keyboard).");
        logit( "ERROR: Failed to read() from stdin (keyboard).\n");
        return 0;
      }

      // EOF on keyboard?
      else if( n_send == 0 ){
        logit( "INFO: EOF on stdin (keyboard).\n");
        return 0;
      }

      // Send everything that has been read.
      else{
        if( send_buf( sock, buf, (int)n_send ) != 0 ){
          return 1;
        }
      }
    } // Data to send.
    
  } // Loop forever.

  // Close socket and return condition code 0.
  close(sock);
  return 0;
}
