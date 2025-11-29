# Verification Plan for Priority Fixes

## 1. Test Polygon Fee Estimation Fallback

**Goal:** Verify that Polygon deployments use fallback "Fast" fees (150 Gwei) when API estimation fails.

### Steps:
1. Deploy a token on Polygon (MATIC_POLYGON) from the UI
2. Check backend logs for:
   ```
   ⚠️  Fee estimation failed: ...
   Using fallback 'Fast' fee for MATIC
   ```
3. Verify deployment completes successfully
4. Check Cobo dashboard to confirm gas fees used (~150 Gwei)
5. Compare transaction speed with previous deployments

**Expected Result:** Deployment succeeds with consistent "Fast" gas prices even if API estimation fails.

---

## 2. Test Error Handling & User Feedback

**Goal:** Verify that deployment errors are displayed properly in the UI.

### Steps:
1. **Test Invalid Input:**
   - Try deploying with empty name/symbol
   - Should see error in red box with dismiss button

2. **Test Network Error:**
   - Stop backend temporarily
   - Try deployment
   - Should see connection error message

3. **Test Cobo Error:**
   - Use invalid wallet ID in .env temporarily
   - Should see structured error with error type

4. **Verify Error Dismissal:**
   - Click X button
   - Error should disappear
   - Can retry deployment

**Expected Result:** All errors show in ErrorDisplay component with helpful messages.

---

## 3. Test Dynamic Wallet Selection

**Goal:** Verify that wallet ID is loaded from environment variable.

### Steps:
1. Check that `.env` has `COBO_DEFAULT_WALLET_ID=<actual_id>`
2. Search codebase for hardcoded wallet ID:
   ```bash
   grep -r "07f7a5de-b138-4f80-a299-9f66450624d5" backend/
   ```
   Should ONLY appear in `settings.py` as default value

3. Deploy token on both BSC and Polygon
4. Check logs confirm wallet ID from settings is used
5. Try changing wallet ID in `.env` (if you have multiple wallets)
6. Restart backend and verify new wallet is used

**Expected Result:** No hardcoded wallet IDs in business logic, all references use `settings.cobo_default_wallet_id`.

---

## Combined Integration Test

**Scenario:** Deploy ERC1400 token on Polygon with all fixes active

### Test Flow:
1. Open UI at `http://localhost:5173`
2. Click "Deploy New Token"
3. Fill in:
   - Name: "Test Priority Fixes"
   - Symbol: "TPF1"
   - Network: Polygon (MATIC)
   - Mode: MANAGED
   - Partitions: "Class A", "Class B"
4. Click Deploy
5. Observe:
   - Backend logs show fee fallback (if estimation fails)
   - Logs show correct wallet ID from settings
   - UI shows pending status
   - No errors displayed (unless genuine issue)
6. Wait for confirmation
7. Verify:
   - Status updates to "Deployed"
   - Contract address is correct
   - Link to PolygonScan works
   - Transaction used ~150 Gwei gas

**Success Criteria:**
- ✅ Deployment completes in <3 minutes
- ✅ Correct wallet used from settings
- ✅ Fallback fees applied for Polygon
- ✅ No hardcoded IDs in code
- ✅ Errors (if any) display properly in UI

---

## Rollback Plan

If any issues found:
1. **Fee Fallback:** Can be disabled by removing exception handling
2. **Error Display:** Revert to alert() temporarily
3. **Wallet Settings:** Hardcode again if .env fails

All changes are non-breaking and can be reverted independently.
