#!/bin/bash
# Full live test of OMNI WIKI — starts the server, runs all tests, reports.
set -m
cd /home/z/my-project

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  OMNI WIKI — FULL LIVE TEST                               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Kill any existing servers
pkill -f "next dev" 2>/dev/null
pkill -f "bun run dev" 2>/dev/null
sleep 2
rm -rf .next

# Start sync service
pgrep -f "sync-service" > /dev/null || (cd mini-services/sync-service && setsid bash -c 'exec bun run dev' > sync-service.log 2>&1 &)

# Start dev server
setsid bash -c 'exec bun run dev' > dev.log 2>&1 &
DEV_PID=$!

echo "[1/12] Starting dev server (PID $DEV_PID)..."
for i in $(seq 1 20); do
  if curl -s -o /dev/null http://localhost:3000/ 2>/dev/null; then break; fi
  sleep 1
done

if ! curl -s -o /dev/null http://localhost:3000/ 2>/dev/null; then
  echo "FAIL: server did not start"
  exit 1
fi
echo "  ✓ Server is up"
echo ""

PASS=0
FAIL=0
ok()   { echo "  ✓ $1"; PASS=$((PASS+1)); }
bad()  { echo "  ✗ $1"; FAIL=$((FAIL+1)); }

echo "[2/12] Seed vault"
if curl -sf -X POST http://localhost:3000/api/seed > /dev/null; then ok "vault seeded"; else bad "seed failed"; fi
echo ""

echo "[3/12] Auth: ensure demo user"
DEMO=$(curl -sf -c /tmp/c.txt -X POST http://localhost:3000/api/auth/ensure-default)
if echo "$DEMO" | grep -q "demo@omniwiki.app"; then ok "demo user created/signed-in"; else bad "ensure-default: $DEMO"; fi
echo ""

echo "[4/12] Auth: GET /api/auth/me"
ME=$(curl -sf -b /tmp/c.txt http://localhost:3000/api/auth/me)
USERID=$(echo "$ME" | python3 -c "import json,sys;print(json.load(sys.stdin)['user']['id'])" 2>/dev/null)
if [ -n "$USERID" ]; then ok "authenticated as $USERID"; else bad "me: $ME"; fi
echo ""

echo "[5/12] Vault: list notes tree"
TREE=$(curl -sf http://localhost:3000/api/notes)
NCOUNT=$(echo "$TREE" | python3 -c "
import json,sys
d=json.load(sys.stdin)
def c(n):
    r=0
    for x in n:
        if 'children' in x: r+=c(x['children'])+c(x['notes'])
        else: r+=1
    return r
print(c(d['tree']))
" 2>/dev/null)
if [ -n "$NCOUNT" ] && [ "$NCOUNT" -gt 0 ]; then ok "$NCOUNT notes in tree"; else bad "tree: empty"; fi
BCOUNT=$(echo "$TREE" | python3 -c "import json,sys;print(len(json.load(sys.stdin)['bookmarks']))" 2>/dev/null)
TCOUNT=$(echo "$TREE" | python3 -c "import json,sys;print(len(json.load(sys.stdin)['tags']))" 2>/dev/null)
ok "$BCOUNT bookmarks, $TCOUNT tags"
echo ""

echo "[6/12] Vault: get single note"
NOTEID=$(echo "$TREE" | python3 -c "
import json,sys
d=json.load(sys.stdin)
def f(n):
    for x in n:
        if 'children' in x:
            r=f(x['children']) or f(x['notes'])
            if r: return r
        elif x['title']=='Welcome to OMNI WIKI': return x['id']
    return None
print(f(d['tree']))
" 2>/dev/null)
if curl -sf http://localhost:3000/api/notes/$NOTEID | grep -q "Welcome"; then ok "fetched note $NOTEID"; else bad "note fetch"; fi
echo ""

echo "[7/12] Search: query 'brain'"
SR=$(curl -sf "http://localhost:3000/api/search?q=brain")
SRCOUNT=$(echo "$SR" | python3 -c "import json,sys;print(len(json.load(sys.stdin)['results']))" 2>/dev/null)
if [ -n "$SRCOUNT" ] && [ "$SRCOUNT" -gt 0 ]; then ok "$SRCOUNT search results for 'brain'"; else bad "search: $SR"; fi
echo ""

echo "[8/12] Graph: nodes + links"
GR=$(curl -sf http://localhost:3000/api/graph)
GNCOUNT=$(echo "$GR" | python3 -c "import json,sys;d=json.load(sys.stdin);print(f'{len(d[\"nodes\"])} nodes, {len(d[\"links\"])} links')" 2>/dev/null)
if [ -n "$GNCOUNT" ]; then ok "$GNCOUNT"; else bad "graph"; fi
echo ""

echo "[9/12] Auth: register + login"
REG=$(curl -sf -X POST http://localhost:3000/api/auth/register -H "Content-Type: application/json" -d '{"email":"tester@omniwiki.app","password":"test1234","name":"Tester"}')
if echo "$REG" | grep -q '"ok":true'; then ok "registered tester@omniwiki.app"; else bad "register: $REG"; fi
LOGIN=$(curl -sf -X POST http://localhost:3000/api/auth/login -H "Content-Type: application/json" -d '{"email":"demo@omniwiki.app","password":"demo1234"}')
if echo "$LOGIN" | grep -q '"ok":true'; then ok "login as demo"; else bad "login: $LOGIN"; fi
echo ""

echo "[10/12] AI Chat: create session + send message"
SID=$(curl -sf -b /tmp/c.txt -X POST http://localhost:3000/api/chat/sessions -H "Content-Type: application/json" -d "{\"userId\":\"$USERID\",\"title\":\"AI test\"}" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])" 2>/dev/null)
if [ -n "$SID" ]; then ok "chat session $SID"; else bad "session create"; fi
CHATOUT=$(timeout 50 curl -s -b /tmp/c.txt -N -X POST http://localhost:3000/api/chat/send -H "Content-Type: application/json" -d "{\"sessionId\":\"$SID\",\"message\":\"What notes about AI do I have?\",\"userId\":\"$USERID\"}" 2>/dev/null)
if echo "$CHATOUT" | grep -q "event: token"; then
  REPLY=$(echo "$CHATOUT" | grep "^event: token" -A1 | tail -1 | sed 's/^data: //')
  ok "AI responded: $(echo $REPLY | head -c 80)..."
else
  bad "AI chat: no token event"
fi
echo ""

echo "[11/12] Librarian: ingest source → proposals → approve → apply"
SRC=$(curl -sf -b /tmp/c.txt -X POST http://localhost:3000/api/chat/sources -H "Content-Type: application/json" -d "{\"userId\":\"$USERID\",\"title\":\"Test Paper\",\"kind\":\"paper\",\"content\":\"Graph neural networks operate on graph-structured data using message passing. Each node aggregates features from neighbors. This enables learning on social networks, molecules, and knowledge graphs.\",\"autoProcess\":true}")
PCOUNT=$(echo "$SRC" | python3 -c "import json,sys;print(json.load(sys.stdin).get('proposals',0))" 2>/dev/null)
if [ -n "$PCOUNT" ] && [ "$PCOUNT" -gt 0 ]; then ok "librarian generated $PCOUNT proposals"; else bad "librarian: $SRC"; fi
PID=$(curl -sf "http://localhost:3000/api/chat/proposals?userId=$USERID&status=pending" | python3 -c "import json,sys;print(json.load(sys.stdin)['proposals'][0]['id'])" 2>/dev/null)
DEC=$(curl -sf -b /tmp/c.txt -X POST "http://localhost:3000/api/chat/proposals/$PID/decide" -H "Content-Type: application/json" -d '{"decision":"approved"}')
if echo "$DEC" | grep -q "approved"; then ok "proposal approved"; else bad "decide: $DEC"; fi
APPLY=$(curl -sf -b /tmp/c.txt -X POST http://localhost:3000/api/chat/proposals/apply -H "Content-Type: application/json" -d "{\"userId\":\"$USERID\"}")
ACOUNT=$(echo "$APPLY" | python3 -c "import json,sys;print(len(json.load(sys.stdin)['applied']))" 2>/dev/null)
if [ -n "$ACOUNT" ] && [ "$ACOUNT" -gt 0 ]; then ok "applied $ACOUNT note(s) to vault"; else bad "apply: $APPLY"; fi
echo ""

echo "[12/12] Agent log"
LOG=$(curl -sf http://localhost:3000/api/chat/log)
LCOUNT=$(echo "$LOG" | python3 -c "import json,sys;print(len(json.load(sys.stdin)['logs']))" 2>/dev/null)
if [ -n "$LCOUNT" ] && [ "$LCOUNT" -gt 0 ]; then ok "$LCOUNT agent log entries"; else bad "log: $LOG"; fi
echo ""

echo "════════════════════════════════════════════════════════"
echo "  RESULT: $PASS passed, $FAIL failed"
echo "════════════════════════════════════════════════════════"

# Verify server still alive
if curl -s -o /dev/null http://localhost:3000/ 2>/dev/null; then
  echo "  ✓ Server still alive after all tests"
else
  echo "  ✗ Server crashed during tests"
fi
