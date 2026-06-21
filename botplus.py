import os
import discord
import json
import random
import asyncio
import io
import urllib.request
import urllib.parse
import datetime
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()                 

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG & INTENTS (CHỈ KHỞI TẠO 1 LẦN)
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Quan trọng: Cần bật trong Discord Developer Portal luôn nhé sếp

# Sử dụng commands.Bot để vừa dùng được event, vừa dùng được Slash Command (tree)
client = commands.Bot(command_prefix='!', intents=intents)
tree = client.tree

# Cấu hình Web Server giữ bot 24/7
app = Flask('')

@app.route('/')
def home():
    return "Bot đang chạy 24/7!"

def run_web_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# Các ID cấu hình cố định
WELCOME_CHANNEL_ID = 1515048941161414836 
ID_KENH_CFS = 1515196032689111171 
ID_ADMIN_TOI_CAO = 1253562031127138371
ID_KENH_BAY_HAI_TAC = 1515048088048504923
ID_SERVER_CUA_BAN = 1506938436668625090

# Bảng phân loại ID Role sinh vật biển
BANG_PHAN_LOAI = {
    1512080326229360650: {"loai": "Whale", "dac_diem": "Giọng ca của đại dương","danh_sach_ten": ["Leviathan", "Stella", "Nova", "Siren"]},
    1512080333674385541: {"loai": "Jellyfish", "dac_diem": "Vũ công vô định","danh_sach_ten": ["Pearl", "Tiny", "Heri", "Mabel"]},
    1512080335788183623: {"loai": "Starfish", "dac_diem": "Ngôi sao rạn san hô","danh_sach_ten": ["Spike", "Claire", "Shimi", "Neero"]},
    1516133639300055153: {"loai": "Octopus", "dac_diem": "Thiên tài ngụy trang","danh_sach_ten": ["Abyss", "Kraken", "Venom", "Shadow"]},
    1512080300442652782: {"loai": "Dolphin", "dac_diem": "Vận động viên lướt sóng","danh_sach_ten": ["Helen", "Kuwa", "Maelle", "Luna"]},
    1512080314854281267: {"loai": "Sea Turtle", "dac_diem": "Nhà du hành thông thái","danh_sach_ten": ["Mixi", "Naito", "Ura", "Bimo"]},
    1512080310014181376: {"loai": "Crab", "dac_diem": "Chiến thần ngang ngược","danh_sach_ten": ["Verso", "Leon", "Haku", "Shiro"]},
    1512080307153535148: {"loai": "Penguin", "dac_diem": "Quý tộc vùng băng giá","danh_sach_ten": ["Bel", "Squishy", "Nibble", "Alex"]},
}

# ==========================================
# 2. KHỔI TẠO AI VÀ NHÂN CÁCH (LORE)
# ==========================================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AQ.Ab8RN6Ksq8B762hDLnfkQWOjMSbU2S3QbXsKBtzSnPczkpLRPw')
genai.configure(api_key=GEMINI_API_KEY)

tat_kiem_duyet = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

kieu_nhan_cach = """
Bạn là Reze, một AI quản gia thân thiện, ngầu và cực kỳ tinh tế thuộc máy chủ Discord "Ocean Wave".
QUY TẮC CỐT LÕI:
1. Trò chuyện đơn giản/vô tri: Trả lời bay bổng, dùng phép ẩn dụ về biển cả (sóng, rạn san hô...)
2. Tìm kiếm thông tin/Tính toán: Trả lời cực kỳ logic, ngắn gọn, chính xác 100%. Không lan man.
3. Luôn xưng "tui", gọi người chat là "bạn". Không bao giờ nói "Tôi là mô hình AI...".
"""

model = genai.GenerativeModel(
    model_name='gemini-3.5-flash', 
    safety_settings=tat_kiem_duyet,
    system_instruction=kieu_nhan_cach
)

FILE_TRI_NHO = "tri_nho_server.json"
tri_nho_nguoi_dung = {}

def doc_tri_nho():
    if os.path.exists(FILE_TRI_NHO):
        with open(FILE_TRI_NHO, "r", encoding="utf-8") as f: return json.load(f) if os.path.getsize(FILE_TRI_NHO) > 0 else {}
    return {}

def ghi_tri_nho(du_lieu):
    with open(FILE_TRI_NHO, "w", encoding="utf-8") as f: json.dump(du_lieu, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. CÁC LỚP ĐỐI TƯỢNG GIAO DIỆN (UI BUTTONS & MODALS)
# ==========================================
class RepCfsModal(discord.ui.Modal, title='Phản hồi tiếng vọng dưới đáy đại dương 🫧༘⋆'):
    noidung = discord.ui.TextInput(
        label='Nội dung phản hồi (Đảm bảo ẩn danh 100%)',
        style=discord.TextStyle.paragraph,
        placeholder='Nhập lời nhắn của bạn vào đây nhé...',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        message = interaction.message
        thread = message.thread
        if thread is None:
            cfs_title = message.embeds[0].title if message.embeds else "Confession"
            thread = await message.create_thread(name=f"Phản hồi {cfs_title}")
        
        await thread.send(f"💬 **Lời hồi đáp của một cư dân đại dương:**\n*{self.noidung.value}*")
        await interaction.response.send_message("🌊 Bạn đã hồi âm tiếng vọng đến từ đại dương", ephemeral=True)

class CfsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="Gửi lời hồi đáp", style=discord.ButtonStyle.primary, emoji="<:repcfs:1197199055290376252>", custom_id="btn_rep_cfs")
    async def btn_reply(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RepCfsModal())

class SendCfsModal(discord.ui.Modal, title='𓆉⋆.˚Lan tỏa âm vang của bạn⋆.˚𓆟'):
    noidung = discord.ui.TextInput(
        label='Âm vang bạn muốn truyền tải (Ẩn danh 100%)',
        style=discord.TextStyle.paragraph,
        placeholder='Trút bầu tâm sự của bạn vào đây nhé...',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        kenh_tam_su = interaction.client.get_channel(ID_KENH_CFS)
        if kenh_tam_su is None:
            await interaction.response.send_message("⚠️ Lỗi: Không tìm thấy ID kênh tâm sự. Vui lòng báo Admin!", ephemeral=True)
            return

        kho = doc_tri_nho()
        so_cfs = kho.get("cfs_count", 0) + 1
        kho["cfs_count"] = so_cfs
        ghi_tri_nho(kho)

        embed = discord.Embed(
            title=f"𓆡⋆.°🐚⋆ Âm vang #{so_cfs} đến từ đại dương ˖°🫧",
            description=f"*{self.noidung.value}*",
            color=0x7cd0e6,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="🐟⋆｡𖦹°・Tiếng lòng của một cư dân ẩn danh・🫧⋆.ೃ࿔*:･")

        await kenh_tam_su.send(embed=embed, view=CfsView())
        await interaction.response.send_message(f"𓆝⋆.˚ Âm vang **#{so_cfs}** của bạn đã được lan tỏa khắp đại dương, hãy chờ hồi đáp nhé.ೃ࿔*", ephemeral=True)
        try:
            admin = await interaction.client.fetch_user(ID_ADMIN_TOI_CAO)
            await admin.send(f"🕵️ **BÁO CÁO MẬT - Âm Vang #{so_cfs}**\n👤 Gửi qua giao diện Nút Bấm/Slash\nTác giả: **{interaction.user.name}** (ID: `{interaction.user.id}`)")
        except: pass

class SetupCfsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="Lan tỏa âm vang", style=discord.ButtonStyle.success, emoji="🐚", custom_id="btn_gui_cfs_chung")
    async def btn_gui_cfs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SendCfsModal())

class LapDoiView(discord.ui.View):
    def __init__(self, host: discord.Member, ten_game: str, so_luong: int, bac_rank: str, noi_dung:str):
        super().__init__(timeout=None)
        self.host = host
        self.ten_game = ten_game
        self.so_luong = so_luong
        self.danh_sach = [host] 
        self.bac_rank = bac_rank 
        self.noi_dung = noi_dung

    def tao_embed(self):
        ds_text = "\n".join([f"**{i+1}.** {m.mention}" for i, m in enumerate(self.danh_sach)])
        phong_voice_text = "Chưa kết nối kênh voice"
        if self.host.voice and self.host.voice.channel:
            phong_voice_text = self.host.voice.channel.mention

        embed = discord.Embed(
            title=f"🪼⋆.Chiêu mộ thành viên cùng chơi game࿔*:･",
            description=(
                f"**۶ৎ Người tạo:** {self.host.mention}\n\n"
                f"**࣪꣑ৎ Trò chơi hiện tại:** {self.ten_game}\n\n"
                f"**... Bậc rank:** {self.bac_rank}\n\n"
                f"**... Phòng game hiện tại:** {phong_voice_text}\n\n"
                f"**... Số lượng:** {len(self.danh_sach)}/{self.so_luong}\n\n"
                f"**... Nội dung:** {self.noi_dung}\n\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"**... Danh sách tham gia:**\n{ds_text}"
            ),
            color=0x7cd0e6
        )
        embed.set_footer(text="Thành viên đã đủ! Get gooooo~" if len(self.danh_sach) >= self.so_luong else "Hàng chờ vẫn đang mở, bấm để tham gia nhé")
        return embed

    @discord.ui.button(label="Tham gia", style=discord.ButtonStyle.success, emoji="⚔️", custom_id="btn_join_lobby")
    async def btn_join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.danh_sach:
            await interaction.response.send_message("Bạn đã trong tổ đội", ephemeral=True)
            return
        if len(self.danh_sach) >= self.so_luong:
            await interaction.response.send_message("Tiếc quá, đội này full slot rồi nha", ephemeral=True)
            return
            
        self.danh_sach.append(interaction.user)
        thong_bao = "Đã tham gia thành công~!"

        if self.host.voice and self.host.voice.channel:
            kenh_voice_host = self.host.voice.channel
            if interaction.user.voice and interaction.user.voice.channel:
                try:
                    await interaction.user.move_to(kenh_voice_host)
                    thong_bao += f"\n🌊 Reze đã tự động dịch chuyển bạn vào phòng cùng đội trưởng!"
                except discord.errors.Forbidden:
                    thong_bao += "\n⚠️ Reze chưa được cấp quyền 'Di chuyển thành viên' (Move Members) để kéo bạn đi."
                except Exception: pass
            else:
                thong_bao += f"\n💡 *Mẹo: Bạn đang ngồi ở một phòng voice bất kỳ thì Reze mới kéo qua {kenh_voice_host.mention} được nha.*"

        await interaction.message.edit(embed=self.tao_embed(), view=self)
        await interaction.response.send_message(thong_bao, ephemeral=True)

    @discord.ui.button(label="Rời đội", style=discord.ButtonStyle.danger, emoji="🚪", custom_id="btn_leave_lobby")
    async def btn_leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.danh_sach:
            await interaction.response.send_message("Bạn hiện không có trong đội này!", ephemeral=True)
            return
            
        if interaction.user == self.host:
            await interaction.message.delete()
            await interaction.response.send_message("🌊 Trưởng đội đã giải tán tổ đội thành công!", ephemeral=True)
            return
            
        self.danh_sach.remove(interaction.user)
        await interaction.message.edit(embed=self.tao_embed(), view=self)
        await interaction.response.send_message("Bạn đã lặng lẽ rời khỏi đội.", ephemeral=True)

# Lệnh slash mẫu Đăng ký lệnh Slash /lapdoi & /cfs
@tree.command(name="cfs", description="🫧⋆ Lan tỏa âm vang của bạn đến đại dương 𓆝⋆.˚")
async def slash_cfs(interaction: discord.Interaction):
    await interaction.response.send_modal(SendCfsModal())

@tree.command(name="lapdoi", description="Lập tổ đội chơi game cực cháy")
@discord.app_commands.describe(
    ten_game="Tên trò chơi (VD: TFT, Valorant)", so_luong="Số người tối đa", bac_rank="Bậc rank yêu cầu", noi_dung="Mô tả ngắn"
)
async def slash_lapdoi(interaction: discord.Interaction, ten_game: str, so_luong: int, bac_rank: str, noi_dung: str):
    if so_luong < 2:
        await interaction.response.send_message("Tổ đội thì phải có ít nhất 2 người!", ephemeral=True)
        return
    view = LapDoiView(host=interaction.user, ten_game=ten_game, so_luong=so_luong, bac_rank=bac_rank, noi_dung=noi_dung)
    await interaction.response.send_message(embed=view.tao_embed(), view=view)

# ==========================================
# 4. HÀM XỬ LÝ VẼ VÀ IN PASSPORT 
# ==========================================
async def in_va_gui_passport(member, role_id):
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    if channel is None: return

    try:
        mau_chu = "#1a365d"
        try:
            font_to = ImageFont.truetype("oceanpixel.otf", 28) 
            font_nho = ImageFont.truetype("oceanpixel.otf", 22)
            font_ki_ten = ImageFont.truetype("chuky.otf", 38)
        except:
            font_to = font_nho = font_ki_ten = ImageFont.load_default()
            print("⚠️ Cảnh báo: Không tìm thấy file font chữ.")
            
        img = Image.open("passport.jpg").convert("RGBA")
        draw = ImageDraw.Draw(img)

        loai_nguoi_dung = BANG_PHAN_LOAI[role_id]["loai"]
        dac_diem = BANG_PHAN_LOAI[role_id]["dac_diem"]
        ten_ca_the_random = random.choice(BANG_PHAN_LOAI[role_id]["danh_sach_ten"])

        ten_hien_thi = member.display_name
        ngay = datetime.datetime.now().strftime("%d/%m/%Y")
        onlyngay = datetime.datetime.now().strftime("%d")
        thu_tu = len(member.guild.members)
        so_ho_chieu = f"{random.randint(0, 999):03d}-{random.randint(0, 999):03d}-{random.randint(0, 999):03d}"

        draw.text((110, 44), "VIP", fill=mau_chu, font=font_to)
        draw.text((175, 71), so_ho_chieu, fill=mau_chu, font=font_to)
        draw.text((233, 390), ten_hien_thi, fill=mau_chu, font=font_to)
        draw.text((221, 430), ngay, fill=mau_chu, font=font_to)
        draw.text((119, 472), loai_nguoi_dung, fill=mau_chu, font=font_to)
        draw.text((163, 514), "Ocean Wave", fill=mau_chu, font=font_to)
        draw.text((170, 549), "Reze", fill=mau_chu, font=font_ki_ten)
        
        draw.text((739, 139), ten_ca_the_random, fill=mau_chu, font=font_to)
        draw.text((562, 248), dac_diem, fill=mau_chu, font=font_to)
        draw.text((698, 519), f"No.{thu_tu}", fill=mau_chu, font=font_to)
        draw.text((875, 519), onlyngay, fill=mau_chu, font=font_to)
        draw.text((805, 621), "Quản lý Reze", fill="#ffffff", font=font_ki_ten) 
        
        if member.display_avatar:
            avatar_req = urllib.request.Request(str(member.display_avatar.url), headers={'User-Agent': 'Mozilla/5.0'})
            avatar_img = Image.open(io.BytesIO(urllib.request.urlopen(avatar_req).read())).convert("RGBA")
            SIZE_AV = 182 
            avatar_img = avatar_img.resize((SIZE_AV, SIZE_AV), Image.Resampling.LANCZOS)
            mask = Image.new("L", (SIZE_AV, SIZE_AV), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, SIZE_AV, SIZE_AV), fill=255)
            img.paste(avatar_img, (77, 131), mask)
        
        with io.BytesIO() as binary:
            img.convert("RGB").save(binary, 'JPEG', quality=95)
            binary.seek(0)
            file_passport = discord.File(binary, filename='passport.jpg')
            
            embed = discord.Embed(
                title="🌊 HỘ CHẤU CƯ DÂN ĐẠI DƯƠNG 🐚",
                description=(
                    f"Giữa đêm mưa gió bùng, {member.mention} bị cuốn trôi rơi vào **𝓞𝓬𝓮𝓪𝓷 𝓦𝓪𝓿𝓮** ✨\n\n"
                    f"⋅‧ ⟡ ‧₊˚┆<#1516117766409683075> - Xem qua luật lệ\n"
                    f"⋅‧ ⟡ ⁠‧₊˚┆<#1511001081117937755> - Nhận role cá nhân\n"
                    f"˚₊‧ ⟡ .࿔:･┆<#1515053474683813918> - Giới thiệu bản thân\n"
                    f"˚₊‧ ⟡ ⋆.࿔:･┆<#1515051548034601020> - Kênh hỗ trợ\n"
                ),
                color=0x7cd0e6
            )
            embed.set_image(url="attachment://passport.jpg")
            await channel.send(embed=embed, file=file_passport)
            
    except Exception as e: 
        print(f"⚠️ Lỗi khi in Passport: {e}")

# ==========================================
# 5. CÁC SỰ KIỆN CHÍNH (EVENTS)
# ==========================================
@client.event
async def on_ready():
    client.add_view(CfsView())
    client.add_view(SetupCfsView())
    MY_GUILD = discord.Object(id=ID_SERVER_CUA_BAN)
    tree.copy_global_to(guild=MY_GUILD)
    await tree.sync(guild=MY_GUILD)
    print(f'[HỆ THỐNG] Dòng chảy lưu thông! Bot {client.user} đã sẵn sàng 🌊')

# SỰ KIỆN 1: Có người mới đặt chân tham gia Server (Tự động gửi tin chào mừng)
@client.event
async def on_member_join(member):
    print(f"📥 {member.name} vừa tham gia server.")
    
    # Tìm kênh welcome dựa trên cấu hình ID của sếp
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        # Tạo một lời chào mừng bằng chữ dễ thương từ Reze gửi ngay lập tức
        embed_welcome = discord.Embed(
            title="🫧 NĂNG LƯỢNG MỚI ĐỔ VỀ ĐẠI DƯƠNG 🌊",
            description=f"Chào mừng cư dân mới {member.mention} đã bị sóng đánh trôi dạt vào **Ocean Wave**!\n\n> Hãy ghé qua <#1511001081117937755> để chọn một loài **Sinh vật biển** định cư và Reze sẽ cấp Hộ chiếu thông hành ngay lập tức nha! 🐳",
            color=0x7cd0e6,
            timestamp=datetime.datetime.now()
        )
        embed_welcome.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
        embed_welcome.set_footer(text=f"Thành viên thứ {len(member.guild.members)} bước vào Ocean Wave")
        await channel.send(content=f"Hey Yo! Cả nhà ơi ra đón người mới nèee {member.mention} 🎉", embed=embed_welcome)

# SỰ KIỆN 2: Thành viên thay đổi Role (Cấp passport)
@client.event
async def on_member_update(before, after):
    roles_moi = [role for role in after.roles if role not in before.roles]
    if not roles_moi: return

    for role in roles_moi:
        if role.id in BANG_PHAN_LOAI:
            await in_va_gui_passport(after, role.id)
            break

# SỰ KIỆN 3: Đọc và Xử lý tin nhắn chat công cộng / DM
@client.event
async def on_message(message):
    if message.author.bot: return

    # LỆNH ẨN GIẢ LẬP CÓ NGƯỜI VÀO SERVER (.testjoin)
    if message.content == ".testjoin":
        if not message.author.guild_permissions.administrator: return
        await message.channel.send("📥 *Đang giả lập tín hiệu có thành viên mới bước qua cửa hải quan Ocean Wave...*")
        
        # Ép bot kích hoạt trực tiếp hàm on_member_join phía trên bằng chính nick của sếp
        client.dispatch('member_join', message.author)
        return

    # LỆNH TEST WELCOME THỦ CÔNG (IN PASSPORT MẪU)
    if message.content == ".testwlc":
        # Tìm xem sếp có đang sở hữu role sinh vật biển nào trong cấu hình không
        role_id_hop_le = None
        for role in message.author.roles:
            if role.id in BANG_PHAN_LOAI:
                role_id_hop_le = role.id
                break
        
        # Nếu sếp không có role nào, bot tự bốc bừa role đầu tiên (Whale) để test mẫu
        if not role_id_hop_le:
            role_id_hop_le = list(BANG_PHAN_LOAI.keys())[0]
            await message.channel.send(f"💡 *Mẹo: Sếp chưa sở hữu role đại dương nào, Reze dùng mẫu role `{BANG_PHAN_LOAI[role_id_hop_le]['loai']}` để in thử nhé!*")

        await message.channel.send("🌊 *Reze đang múc nước biển pha mực in... Tiến hành xuất xưởng hộ chiếu thử nghiệm!*")
        
        # Gọi hàm in passport bằng chính profile của sếp
        await in_va_gui_passport(message.author, role_id_hop_le)
        return

    # .setupbait
    if message.content == ".setupbait":
        if not message.author.guild_permissions.administrator: return 
        embed = discord.Embed(title="⚠️ **THE ABYSS** ⚠️", description="Kênh thuần chống spam, không nhắn tin vào đây.", color=0xff0000)
        embed.set_image(url="https://i.pinimg.com/736x/c2/48/6f/c2486fce2ffc0d5264c341495443e0fb.jpg") 
        await message.channel.send(embed=embed)
        await message.delete() 
        return

    # Bẫy Honeypot tự động Ban nick spam link độc
    if message.channel.id == ID_KENH_BAY_HAI_TAC:
        if message.author.guild_permissions.administrator: return
        try:
            await message.delete()
            await message.author.ban(reason="Lọt bẫy hải tặc.", delete_message_days=7)
            try:
                admin = await client.fetch_user(ID_ADMIN_TOI_CAO)
                await admin.send(f"🚨 Tài khoản **{message.author.name}** vừa bị ban vì lọt bẫy!")
            except: pass
        except discord.errors.Forbidden:
            print("⚠️ Reze thiếu quyền ban người này.")
        return

    # Confession qua tin nhắn riêng (.gui)
    if isinstance(message.channel, discord.DMChannel) and message.content.startswith('.gui'):
        noidung_tam_su = message.content.replace('.gui', '').strip()
        if not noidung_tam_su:
            await message.reply("🐚 Bạn quên gửi gắm nội dung rồi!")
            return

        kenh_tam_su = client.get_channel(ID_KENH_CFS)
        if kenh_tam_su is None: return

        kho = doc_tri_nho()
        so_cfs = kho.get("cfs_count", 0) + 1
        kho["cfs_count"] = so_cfs
        ghi_tri_nho(kho)

        embed = discord.Embed(title=f"𓆡⋆.°🐚⋆ Âm vang #{so_cfs} ˖°🫧", description=f"*{noidung_tam_su}*", color=0x7cd0e6, timestamp=datetime.datetime.now())
        await kenh_tam_su.send(embed=embed, view=CfsView())
        await message.reply(f"𓆝⋆.˚ Âm vang **#{so_cfs}** đã được lan tỏa!")
        try:
            admin = await client.fetch_user(ID_ADMIN_TOI_CAO)
            await admin.send(f"🕵️ **CFS #{so_cfs}** từ DM của **{message.author.name}**")
        except: pass
        return

    # .setupcfs
    if message.content == ".setupcfs":
        if not message.author.guild_permissions.administrator: return 
        embed = discord.Embed(title="⋅˚₊‧🐚 LAN TỎA TIẾNG VỌNG ଳ⋆.࿔*", description="Ấn nút bên dưới để gửi ẩn danh.", color=0x7cd0e6)
        embed.set_image(url="https://i.pinimg.com/736x/58/75/b1/5875b163b15f92ec3ba41efde14cd3d1.jpg")      
        await message.channel.send(embed=embed, view=SetupCfsView())
        await message.delete() 
        return

    # .setuplapdoi
    if message.content == ".setuplapdoi":
        if not message.author.guild_permissions.administrator: return 
        embed = discord.Embed(title="⋆.°・LẬP TEAM CHIẾN GAME・˖°🪼", description="Sử dụng lệnh `/lapdoi` để tuyển thành viên.", color=0x7cd0e6)
        embed.set_image(url="https://i.pinimg.com/736x/6f/f7/06/6ff7065d1272a10929111e3c27f9f5fd.jpg")
        await message.channel.send(embed=embed)
        await message.delete()
        return

    # Tính năng học từ khóa: .r học: A = B
    if message.content.startswith('.r học:'):
        noidung_hoc = message.content.replace('.r học:', '').split('=')
        if len(noidung_hoc) == 2:
            kho = doc_tri_nho()
            kho[noidung_hoc[0].strip().lower()] = noidung_hoc[1].strip()
            ghi_tri_nho(kho)
            await message.reply(f"✅ Đã lưu từ khóa: **{noidung_hoc[0].strip()}**")
        else:
            await message.reply("⚠️ Cú pháp: `.r học: [Từ khóa] = [Ý nghĩa]`")
        return

    # Chat AI (.p)
    if message.content.startswith('.p'):
        user_question = message.content.replace('.p', '').strip()
        user_id = message.author.id
        if not user_question: return
            
        if user_id not in tri_nho_nguoi_dung: tri_nho_nguoi_dung[user_id] = model.start_chat(history=[])
        
        du_lieu_thoi_tiet = ""
        if "thời tiết" in user_question.lower():
            try:
                cac_tu_thua = ["dự báo", "thời tiết", "hôm nay", "ngày mai", "hiện tại", "tại", "ở", "khu vực"]
                chuoi_dia_diem = user_question.lower()
                for tu in cac_tu_thua: chuoi_dia_diem = chuoi_dia_diem.replace(tu, "")
                thanh_pho = chuoi_dia_diem.strip().replace(" ", "_")
                if thanh_pho:
                    url = urllib.parse.quote(f"https://wttr.in/{thanh_pho}?format=3", safe=":/=?&")
                    thoi_tiet = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=5).read().decode().strip()
                    du_lieu_thoi_tiet = f"\n[Thời tiết hiện tại]: {thoi_tiet}"
            except: pass

        kien_thuc = "\n".join([f"- {k}: {v}" for k, v in doc_tri_nho().items()])
        prompt = f"[HƯỚNG DẪN]: Hôm nay là {datetime.datetime.now().strftime('%d/%m/%Y')}. {du_lieu_thoi_tiet}\n[TỪ ĐIỂN]: {kien_thuc}\n\n[CÂU HỎI]: {user_question}"
        
        try:
            async with message.channel.typing():
                response = await tri_nho_nguoi_dung[user_id].send_message_async(prompt)
                await message.reply(response.text)
        except Exception as e:
            await message.reply(f"⚠️ Sóng yếu: {e}")

    # Đảm bảo lệnh Slash hoạt động song song với on_message
    await client.process_commands(message)

# ==========================================
# 6. KÍCH HOẠT SERVER VÀ CHẠY BOT
# ==========================================
if __name__ == "__main__":
    t = Thread(target=run_web_server)
    t.start()
    
    TOKEN_BOT = os.getenv('DISCORD_TOKEN')
    if TOKEN_BOT:
        client.run(TOKEN_BOT)
    else:
        print("Lỗi: Không tìm thấy DISCORD_TOKEN trong file .env!")
