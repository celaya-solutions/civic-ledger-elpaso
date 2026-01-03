#!/bin/zsh
(
echo '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"1.0","capabilities":{},"clientInfo":{"name":"local-test-client","version":"0.1"}}}'
sleep 0.2
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
sleep 0.2
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_legal_authority","arguments":{"jurisdiction":"texas","topic":"utility_regulation","query":"Can municipalities regulate water service conditions for industrial users?"}}}'
) | python server.py
