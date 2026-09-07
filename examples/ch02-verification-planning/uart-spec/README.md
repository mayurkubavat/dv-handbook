# UART transmitter and receiver: specification (for exercises 1 and 2)

This is a deliberately ordinary one-page specification of the kind a
verification engineer is handed. It contains requirements that are not
marked as requirements. Your task in the exercises is to find them all.

## Overview

The block is a universal asynchronous receiver/transmitter with one transmit
and one receive channel. It connects to a host through a register interface
and to the outside world through the `txd` and `rxd` pins. Data is 8 bits,
with one start bit, one stop bit and optional even or odd parity. The baud
rate is programmable through a 16-bit divisor of the system clock, and the
receiver oversamples each bit 16 times.

## Registers

| Offset | Name | Access | Description |
|---|---|---|---|
| 0x00 | DATA | R/W | Write: enqueue a byte for transmission. Read: dequeue a received byte. |
| 0x04 | STATUS | R | Bit 0 TX_EMPTY, bit 1 TX_FULL, bit 2 RX_EMPTY, bit 3 RX_FULL, bit 4 PARITY_ERR, bit 5 FRAME_ERR, bit 6 OVERRUN. |
| 0x08 | CTRL | R/W | Bit 0 TX_EN, bit 1 RX_EN, bit 2 PARITY_EN, bit 3 PARITY_ODD, bits 15:0 unused above bit 3. |
| 0x0C | DIV | R/W | 16-bit baud divisor. Bit period is DIV+1 system clocks. Writing 0 is not allowed. |

Reading STATUS clears PARITY_ERR, FRAME_ERR and OVERRUN. Writing DATA while
TX_FULL is set is ignored. Reading DATA while RX_EMPTY is set returns the
last byte received and does not change the queue.

## Transmit

When TX_EN is set and the transmit queue is not empty, the transmitter
sends the oldest byte least-significant bit first, framed by a start bit
(low) and a stop bit (high), with a parity bit between the data and the stop
bit when PARITY_EN is set. `txd` idles high. Clearing TX_EN in the middle of
a frame completes the frame before stopping. The transmit queue holds eight
bytes.

## Receive

When RX_EN is set, the receiver waits for a falling edge on `rxd`, confirms
the start bit at the middle of the bit period, then samples each following
bit at its middle. A stop bit sampled low sets FRAME_ERR and the byte is
discarded. A parity mismatch sets PARITY_ERR but the byte is kept. A byte
arriving when the receive queue is full sets OVERRUN and is discarded. The
receive queue holds eight bytes. Changing DIV while a frame is in progress
produces undefined results.

## Reset

After reset, both queues are empty, all CTRL bits are 0, DIV is 0x0000 and
`txd` is high.
