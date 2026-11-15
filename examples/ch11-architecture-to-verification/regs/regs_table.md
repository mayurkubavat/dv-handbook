| Version | Offset | Register | Bits | Field | Access | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| v1 | 0x00 | `SRC_ADDR` | 31:0 | `addr` | rw | Source byte address; alignment not checked |
| v1 | 0x04 | `DST_ADDR` | 31:0 | `addr` | rw | Destination byte address; alignment not checked |
| v1 | 0x08 | `XFER_LEN` | 31:0 | `words` | rw | Length in words; only bits 15:0 are counted |
| v1 | 0x0C | `CTRL` | 1 | `irq_en` | rw | Raise IRQ when the transfer ends |
| v1 | 0x0C | `CTRL` | 0 | `start` | rw | Write 1 to start; cleared by hardware |
| v1 | 0x10 | `STATUS` | 2 | `error` | ro | An AXI response was not OKAY |
| v1 | 0x10 | `STATUS` | 1 | `done` | ro | Transfer ended; cleared by the next start |
| v1 | 0x10 | `STATUS` | 0 | `busy` | ro | Transfer running |
| v2 | 0x00 + 0x20 x n | `SRC_ADDR` | 31:2 | `addr` | rw | Source word address |
| v2 | 0x00 + 0x20 x n | `SRC_ADDR` | 1:0 | `zero` | ro | Read as zero: transfers are word-aligned |
| v2 | 0x04 + 0x20 x n | `DST_ADDR` | 31:2 | `addr` | rw | Destination word address |
| v2 | 0x04 + 0x20 x n | `DST_ADDR` | 1:0 | `zero` | ro | Read as zero: transfers are word-aligned |
| v2 | 0x08 + 0x20 x n | `XFER_LEN` | 15:0 | `words` | rw | Length in words, 0 to 65535; 0 ends at once |
| v2 | 0x0C + 0x20 x n | `CTRL` | 1 | `irq_en` | rw | Raise IRQ when this channel ends |
| v2 | 0x0C + 0x20 x n | `CTRL` | 0 | `start` | wo | Write 1 to start; reads as zero |
| v2 | 0x10 + 0x20 x n | `STATUS` | 2 | `error` | w1c | An AXI response was not OKAY; write 1 to clear |
| v2 | 0x10 + 0x20 x n | `STATUS` | 1 | `done` | w1c | Transfer ended; write 1 to clear |
| v2 | 0x10 + 0x20 x n | `STATUS` | 0 | `busy` | ro | Transfer running |
