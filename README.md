Initiator
Listener

Initiator
1. Mengirim poll
2. Menerima response

Listener
1. Menerima poll
2. Mengirim response

Flow Initiator
1. Mengirim pesan poll (MODE ANTENA MENGIRIM)
2. Receive delay after send (parameter 1) (DELAY YG DIPERLUKAN UNTUK TRANSISI KE MODE ANTENNA MENERIMA)
3. Antenna delay timeout (parameter 2) (MODE ANTENA MENERIMA)
4. Menerima response
5. Menghitung ToF

Flow Listener
1. Menyalakan antenna penerima hingga timeout untuk menerima poll (parameter 3)
2. Ngeset deadline pengiriman response (parameter 4)
3. Sebelum deadline, harus berhasil memproses:
    - Mengcopy waktu polling diterima ke buffer UWB
    - Mengcopy waktu deadline/waktu pengiriman response ke buffer UWB

Variabel penghitungan ToF:
1. Waktu pengiriman poll (dicatat oleh initiator)
2. Waktu penerimaan poll (dicatat oleh listener)
3. Waktu pengiriman response (dicatat oleh listener)
4. Waktu penerimaan response (dicatat oleh initiator)


{
    "status":"OK",
    "device_id":"A0A3B31F3994",
    "pan_id":4660,
    "source_address":13107,
    "destination_address":8738,
    "distance":0.96246
}
{
    "status":"OK",
    "device_id":"E05A1B1FAF98",
    "pan_id":4660,
    "source_address":4369,
    "destination_address":13107,
    "distance":1.110378
}
{
    "status":"OK",
    "device_id":"A0A3B31FC848",
    "pan_id":4660,
    "source_address":8738,
    "destination_address":4369,
    "distance":-0.045598
}