import sys, datetime, math
import base91, bitstream, charset, berkeleydbstore
import gmail, utils
from email.utils import parseaddr
import unidecode
from dateutil import parser



class ProcessCommands:
    def __init__(self,data):
        self.data = data
        self.bsi = bitstream.Bitstream(base91.decode(data))
        self.bso = bitstream.Bitstream()
        self.gmail_service = gmail.authenticate_service_account()
        self.ps = berkeleydbstore.BerkeleyDBStore("mimas-agent.db3")

        # write last mail check
        self.bso.write_fixed_width(int(datetime.datetime.now(datetime.timezone.utc).timestamp()), utils.DATE_LENGTH)

    def send(self):
        mimas_id = self.bsi.read_fixed_width(utils.ID_LENGTH)
        to = self.bsi.read_huffman_string()
        to = to.replace('*', '@')
        subject = self.bsi.read_huffman_string()
        body = self.bsi.read_huffman_string()
        message_id = gmail.send_email(self.gmail_service, to, subject, body)
        if message_id:
            self.ps.set(str(mimas_id),str(message_id))
            self.bso.write_fixed_width(utils.RESP_SENT, utils.RESP_LENGTH)
            self.bso.write_fixed_width(mimas_id, utils.ID_LENGTH)        

    def reply(self):
        mimas_new_id = self.bsi.read_fixed_width(utils.ID_LENGTH)
        mimas_id = self.bsi.read_fixed_width(utils.ID_LENGTH)
        body = self.bsi.read_huffman_string()
        gmail_id = self.ps.get(str(mimas_id))
        new_gmail_id = gmail.send_reply(self.gmail_service,gmail_id, body)
        if new_gmail_id:
            self.ps.set(str(mimas_id),str(gmail_id))
            self.bso.write_fixed_width(utils.RESP_SENT, utils.RESP_LENGTH)
            self.bso.write_fixed_width(mimas_new_id, utils.ID_LENGTH)        

    def mark_read(self):
        mimas_id = self.bsi.read_fixed_width(utils.ID_LENGTH)
        msg_id = self.ps.get(str(mimas_id))
        gmail.mark_message_as_read(self.gmail_service, msg_id)
        # add to output
        self.bso.write_fixed_width(utils.RESP_MARKED_READ, utils.RESP_LENGTH)
        # write id
        self.bso.write_fixed_width(mimas_id, utils.ID_LENGTH)


    def check_mail(self):
        timestamp = self.bsi.read_fixed_width(utils.DATE_LENGTH)
        # if timestamp is 0, set it to 2 days ago
        if timestamp == 0:
            timestamp = int((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2)).timestamp())
        max_size = self.bsi.read_fixed_width(utils.MAX_SIZE_LENGTH)
        # if max_size is 0, set it to some reasonable default
        if max_size == 0:
            max_size = 10*1024 # 10kB
        # get new messages since date
        messages = gmail.get_unread_emails(self.gmail_service, timestamp)
        #messages = [{'id': '195d262dbd1b0a6f', 'snippet': 'Dobrý den Ludek Chovanec, vaše objednávka je připravena k vyzvednutí. Dobrý den Ludek Chovanec, vaše objednávka je připravena k vyzvednutí. Kliknutím na tlačítko „Sledovat objednávku“ zobrazíte další', 'from': 'Temu <temu@orders.temu.com>', 'subject': 'Vaše objednávka Temu je\xa0připravena k vyzvednutí (#PO-053-06138133909031412)', 'date': 'Wed, 26 Mar 2025 12:17:26 +0000 (UTC)'}, {'id': '195d26009e93d4b8', 'snippet': 'Vyzvedněte si prosím balíček co nejdříve V zájmu zachování Vašeho soukromí Temu nikdy nezveřejňuje Vaši e-mailovou adresu žádné třetí straně. Máme zabezpečený systém, který Vám automaticky přeposílá e-', 'from': 'Temu <notice@orders.temu.com>', 'subject': 'Váš balíček Temu dorazil na místo vyzvednutí', 'date': 'Wed, 26 Mar 2025 12:14:22 +0000'}, {'id': '195d223973739fac', 'snippet': 'Rejestr jachtów oraz innych jednostek pływających o długości do 24 m Wiadomość wygenerowana automatycznie, prosimy na nią nie odpowiadać Szanowna Pani/Szanowny Panie Na Pani/Pana konto wpłynęło', 'from': 'system@reja24.gov.pl', 'subject': '[REJA24] Powiadomienie o otrzymaniu UPD', 'date': 'Wed, 26 Mar 2025 12:08:19 +0100 (CET)'}, {'id': '195d1fa3795659a2', 'snippet': 'Cześć Ludek Chovanec, tu Twój pociąg! Przyjadę po Ciebie 2025-03-26 na stację Warszawa Wsch. i pojedziemy razem do stacji Opole Gł.. Przygotowałem dla Ciebie miejsce nr 71 w wagonie 7. Poniżej', 'from': 'PKP Intercity <bilet@intercity.pl>', 'subject': '2025-03-26 [Warszawa Wsch. - Opole Gł.] - bilet PKP Intercity nr WN20646663', 'date': 'Wed, 26 Mar 2025 11:23:07 +0100 (CET)'}, {'id': '195c23ac5822dc03', 'snippet': 'geometrie Ludek Chovanec vás zve na událost geometrie, která se koná pondělí 24. bře 2025 ⋅ 10:00 – 11:00 (Středoevropský čas - Curych). Blíží se událost geometrie pondělí 24. bře 2025 ⋅ 10:00 – 11:00', 'from': '"Kalendář Google" <calendar-notification@google.com>', 'subject': 'Oznámení: geometrie - po 24. bře 2025 10:00 - 11:00 (SEČ) (ludek@chovanec.com)', 'date': 'Sun, 23 Mar 2025 08:59:45 +0000'}, {'id': '195b51a43a00902e', 'snippet': 'Dobrý den, pane Chovanec, máme pro Vás údržbu hrobu. Pokud máte zájem, poprosím o potvrzení. Město hrobu: Frýdlant nad Ostravicí Hřbitov: Frýdlant nad Ostravicí Jak hrob najít: Od parkoviště zadní', 'from': '"AndělskéSlužby.cz" <info@andelskesluzby.cz>', 'subject': 'Nová údržba hrobu', 'date': 'Thu, 20 Mar 2025 20:49:09 +0100 (CET)'}, {'id': '195b4b01fe008ab7', 'snippet': 'Hello, here is your boarding pass. Note that fees mentioned will be paid on site by the club. Kind regards ARIANE ROQUEBERT SAILING PASSION ASBL A member of the Luxembourg sailing federation Address:', 'from': '"⛵️ARIANE" <ariane.roquebert@sailingpassion.lu>', 'subject': 'Fwd: Lenka Mediteran Yachting d.o.o. - Boarding pass - ID: 905212525', 'date': 'Thu, 20 Mar 2025 18:52:43 +0100'}]
        #print(messages)
        # make smaller
        # max_size for each message
        if len(messages) > 0:
            msg_max_size = max_size // len(messages) - 5 # id and nuls
            for message in messages:
                #get just the plain e-mail address
                message['from'] = utils.decode_email_address(message['from'])
                #decode subject
                message['subject'] = utils.decode_email_subject(message['subject'])
                #ascify
                message['from'] = utils.str_encode(message['from'])
                message['subject'] = utils.str_encode(message['subject'])
                message['snippet'] = utils.str_encode(message['snippet'])
                length = len(message['from']) + len(message['subject']) + len(message['snippet'])
                if length > msg_max_size:
                    # change proportionally        
                    f, s, sn = utils.scale_numbers(len(message['from']), len(message['subject']), len(message['snippet']), msg_max_size, 20, 40)
                    message['from'] = message['from'][:f]
                    message['subject'] = message['subject'][:s]
                    message['snippet'] = message['snippet'][:sn]

                # assign mimas-id to the messsage
                last_id = self.ps.get("last-msg-id")
                if not last_id:
                    last_id = 0
                mimas_id = int(last_id) + 1
                self.ps.set("last-msg-id", str(mimas_id))

                # link msg id with mimas-id
                self.ps.set(str(mimas_id), message['id'] )

                # add to output
                self.bso.write_fixed_width(utils.RESP_MESSAGE, utils.RESP_LENGTH)
                # write id
                self.bso.write_fixed_width(mimas_id, utils.ID_LENGTH)
                # write date
                self.bso.write_fixed_width(int(parser.parse(message['date']).timestamp()), utils.DATE_LENGTH)
                # write from
                self.bso.write_huffman_string(message['from'])
                # write subject
                self.bso.write_huffman_string(message['subject'])
                # write body
                self.bso.write_huffman_string(message['snippet'])

    def get(self):
        pass

    # CMD_ID HANDLER
    cmd_map = {
        utils.CMD_NONE: lambda x: None,
        utils.CMD_SEND: send,
        utils.CMD_REPLY: reply,
        utils.CMD_MARK_READ: mark_read,
        utils.CMD_CHECK_MAIL: check_mail,
        utils.CMD_GET: get
    }

    def run(self):
        while True:
            try:
                cmd = self.bsi.read_fixed_width(utils.CMD_LENGTH)
            except (IndexError, KeyError):
                break
                # run handler
            self.cmd_map[cmd](self)
        # export the reply and return it
        out = base91.encode(self.bso.export())

        return out            

# get request
# unpack
# read sequentially and perform actions
# when everything is done
# assemble the reply
# pack it
# send it out as reply to the original sender of the request


data = sys.stdin.read()
p = ProcessCommands(data)
output = p.run()

sys.stdout.write(output)

        # SEND NEW_ID TO SUBJECT DATA
        # REPLY NEW_ID ID DATA
        # MARK_READ ID
        # CHECK DATE MAX_SIZE
        # GET ID MAX_SIZE

        # MSG ID DATE FROM SUBJECT DATA
        # SENT ID
