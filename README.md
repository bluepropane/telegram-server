# telegram-server
Telegram server that is able to send/receive messages using a human account + number instead of a bot handle.

### Dependencies
`telegram-server` requires the C-based [telegram-cli](https://github.com/vysheng/tg) to communicate using the Telegram Mobile protocol.
The `telegram-cli` binary file will be compiled from source during initial setup so you just have to run `setup.sh` in the root folder.
If, for some reason, the compilation during setup fails, please follow the instructions on the repo itself (https://github.com/vysheng/tg) and place the compiled folder in the `telegram-server` root folder.
