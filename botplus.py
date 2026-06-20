import discord
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import datetime
import urllib.request
import urllib.parse
import random
import json
import os
import io
import asyncio
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
load_dotenv()                 

# ==========================================
# 1. CẤU HÌNH BẢO MẬT & KÊNH
# ==========================================
# Lấy giá trị Token từ biến môi trường có tên là DISCORD_TOKEN
# 1. Khởi tạo Intents (cần thiết cho các bot hiện đại)
intents = discord.Intents.default()
intents.message_content = True

# 2. Khởi tạo client/bot
client = commands.Bot(command_prefix='!', intents=intents)

# 3. Lấy token từ biến môi trường
token = os.getenv('DISCORD_TOKEN')

# 4. Chạy bot
if token:
    client.run(token)
else:
    print("Lỗi: Không tìm thấy DISCORD_TOKEN trong biến môi trường!")
GEMINI_API_KEY = os.getenv('AQ.Ab8RN6Ksq8B762hDLnfkQWOjMSbU2S3QbXsKBtzSnPczkpLRPw')
WELCOME_CHANNEL_ID = 1515048941161414836 
ID_KENH_CFS = 1515196032689111171 
ID_ADMIN_TOI_CAO = 1253562031127138371
ID_KENH_BAY_HAI_TAC = 1515048088048504923

# ==========================================
# 2. KHỞI TẠO AI VÀ NHÂN CÁCH (LORE)
# ==========================================
genai.configure(api_key="AQ.Ab8RN6Ksq8B762hDLnfkQWOjMSbU2S3QbXsKBtzSnPczkpLRPw")

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
4. TỪ ĐIỂN NHÂN VẬT TỐI MẬT: 
"""

model = genai.GenerativeModel(
    model_name='gemini-3.5-flash', 
    safety_settings=tat_kiem_duyet,
    system_instruction=kieu_nhan_cach
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

FILE_TRI_NHO = "tri_nho_server.json"
tri_nho_nguoi_dung = {}

def doc_tri_nho():
    if os.path.exists(FILE_TRI_NHO):
        with open(FILE_TRI_NHO, "r", encoding="utf-8") as f: return json.load(f)
    return {}

def ghi_tri_nho(du_lieu):
    with open(FILE_TRI_NHO, "w", encoding="utf-8") as f: json.dump(du_lieu, f, ensure_ascii=False, indent=4)

#TINH NANG CFS
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
        
        # Tạo thread mới nếu CFS này chưa có ai phản hồi
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

        # Gửi CFS lên kênh kèm theo nút bấm
        await kenh_tam_su.send(embed=embed, view=CfsView())
        await interaction.response.send_message(f"𓆝⋆.˚ Âm vang **#{so_cfs}** của bạn đã được lan tỏa khắp đại dương, hãy chờ hồi đáp nhé.ೃ࿔*", ephemeral=True)
        # --- TÍNH NĂNG MỚI: BÁO CÁO MẬT CHO ADMIN TỐI CAO ---
        try:
            admin = await interaction.client.fetch_user(ID_ADMIN_TOI_CAO)
            await admin.send(f"🕵️ **BÁO CÁO MẬT - Âm Vang #{so_cfs}**\n👤 Gửi qua giao diện Nút Bấm/Slash\nTác giả: **{interaction.user.name}** (ID: `{interaction.user.id}`)")
        except:
            pass # Bỏ qua nếu có lỗi (ví dụ: lỡ bạn đang khóa DM)
        # ---------------------------------------------------


# Đăng ký lệnh Slash
@tree.command(name="cfs", description="🫧⋆ Lan tỏa âm vang của bạn đến đại dương 𓆝⋆.˚")
async def slash_cfs(interaction: discord.Interaction):
    await interaction.response.send_modal(SendCfsModal())
# Tạo nút bấm
class SetupCfsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="Lan tỏa âm vang", style=discord.ButtonStyle.success, emoji="🐚", custom_id="btn_gui_cfs_chung")
    async def btn_gui_cfs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SendCfsModal())

# ------------------------------------------
# KHỐI GIAO DIỆN BẢNG CÁO THỊ LẬP ĐỘI
# ------------------------------------------
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
        
        # --- LOGIC KIỂM TRA PHÒNG VOICE CỦA ĐỘI TRƯỞNG ---
        phong_voice_text = "Chưa kết nối kênh voice"
        if self.host.voice and self.host.voice.channel:
            # Thuộc tính .mention sẽ tự động biến thành link bấm được
            phong_voice_text = self.host.voice.channel.mention
        # -------------------------------------------------

        embed = discord.Embed(
            title=f"🪼⋆.Chiêu mộ thành viên cùng chơi game࿔*:･",
            description=(
                f"**۶ৎ Người tạo:** {self.host.mention}\n\n"
                f"**࣪꣑ৎ Trò chơi hiện tại:** {self.ten_game}\n\n"
                f"**꣑ৎ Bậc rank:** {self.bac_rank}\n\n"
                f"**꣑ৎ Phòng game hiện tại:** {phong_voice_text}\n\n" # <--- DÒNG HIỂN THỊ VOICE ĐƯỢC THÊM VÀO ĐÂY
                f"**꣑ৎ Số lượng:** {len(self.danh_sach)}/{self.so_luong}\n\n"
                f"**꣑ৎ Nội dung:** {self.noi_dung}\n\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"**꣑ৎ Danh sách tham gia:**\n{ds_text}"
            ),
            color=0x7cd0e6
        )
        
        if len(self.danh_sach) >= self.so_luong:
            embed.set_footer(text="Thành viên đã đủ! Get gooooo~")
        else:
            embed.set_footer(text="Hàng chờ vẫn đang mở, bấm để tham gia nhé")
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

        # --- LOGIC TỰ ĐỘNG DỊCH CHUYỂN ---
        if self.host.voice and self.host.voice.channel:
            kenh_voice_host = self.host.voice.channel
            if interaction.user.voice and interaction.user.voice.channel:
                try:
                    await interaction.user.move_to(kenh_voice_host)
                    thong_bao += f"\n🌊 Reze đã tự động dịch chuyển bạn vào phòng cùng đội trưởng!"
                except discord.errors.Forbidden:
                    thong_bao += "\n⚠️ Reze chưa được cấp quyền 'Di chuyển thành viên' (Move Members) để kéo bạn đi."
                except Exception:
                    pass
            else:
                thong_bao += f"\n💡 *Mẹo: Bạn đang ngồi ở một phòng voice bất kỳ thì Reze mới kéo qua {kenh_voice_host.mention} được nha.*"
        # ---------------------------------

        # Cập nhật lại giao diện bảng (Hàm tao_embed() sẽ quét lại phòng voice mới nhất nếu host có di chuyển)
        await interaction.message.edit(embed=self.tao_embed(), view=self)
        await interaction.response.send_message(thong_bao, ephemeral=True)

    @discord.ui.button(label="Rời đội", style=discord.ButtonStyle.danger, emoji="🚪", custom_id="btn_leave_lobby")
    async def btn_leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.danh_sach:
            await interaction.response.send_message("Bạn hiện không có trong đội này!", ephemeral=True)
            return
            
        # Nâng cấp logic: Nếu đội trưởng bấm nút, bot sẽ tự tay hủy Bảng cáo thị
        if interaction.user == self.host:
            await interaction.message.delete()
            await interaction.response.send_message("🌊 Trưởng đội đã giải tán tổ đội thành công!", ephemeral=True)
            return
            
        # Nếu là thành viên bình thường thì chỉ xóa tên
        self.danh_sach.remove(interaction.user)
        await interaction.message.edit(embed=self.tao_embed(), view=self)
        await interaction.response.send_message("Bạn đã lặng lẽ rời khỏi đội.", ephemeral=True)

# Đăng ký lệnh Slash /lapdoi
@tree.command(name="lapdoi", description="Lập tổ đội chơi game cực cháy")
@discord.app_commands.describe(
    ten_game="Tên trò chơi (VD: TFT, Valorant, FreeFire, CS:GO...)", 
    so_luong="Số người tối đa của đội",
    bac_rank="Bậc rank yêu cầu (VD: Đồng, Bạc, Vàng, Thách Đấu...)",
    noi_dung="Vui vẻ kh quạu, custom vv, try hard nha,..."
)
async def slash_lapdoi(interaction: discord.Interaction, ten_game: str, so_luong: int, bac_rank: str, noi_dung: str):
    if so_luong < 2:
        await interaction.response.send_message("Tổ đội thì phải có ít nhất 2 người chứ cô đơn quá vậy!", ephemeral=True)
        return
        
    view = LapDoiView(host=interaction.user, ten_game=ten_game, so_luong=so_luong, bac_rank=bac_rank, noi_dung=noi_dung)
    await interaction.response.send_message(embed=view.tao_embed(), view=view)

# ==========================================
# 4. SỰ KIỆN: CẤP PASSPORT (Dựa trên Role Update)
# ==========================================
@client.event
async def on_ready():
    client.add_view(CfsView())
    client.add_view(SetupCfsView())
    # 1. Điền ID Server (Guild ID) của Ocean Wave vào đây
    ID_SERVER_CUA_BAN = 1506938436668625090
    MY_GUILD = discord.Object(id=ID_SERVER_CUA_BAN)
    # 2. Ép chép lệnh và đồng bộ ngay lập tức cho server này
    tree.copy_global_to(guild=MY_GUILD)
    await tree.sync(guild=MY_GUILD)
    
    print(f'[HỆ THỐNG] Dòng chảy đã lưu thông! Bot {client.user} đã sẵn sàng 🌊')

@client.event
async def on_member_update(before, after):
    # 1. Lọc ra các Role mới vừa được gắn (So sánh trước và sau khi update)
    roles_moi = [role for role in after.roles if role not in before.roles]
    if not roles_moi:
        return

    # 2. Bảng phân loại ID Role
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

    # 3. Quét kiểm tra: Nếu role vừa thêm thuộc về sinh vật biển thì mới chạy tiếp
    role_dai_duong = None
    for role in roles_moi:
        if role.id in BANG_PHAN_LOAI:
            role_dai_duong = role
            break

    if not role_dai_duong:
        return

    # 4. BẮT ĐẦU VẼ PASSPORT
    WELCOME_CHANNEL_ID = 1515048941161414836 
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
            print("⚠️ Cảnh báo: Không tìm thấy file oceanpixel.otf")
            
        img = Image.open("passport.jpg").convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Trích dữ liệu theo vai trò
        loai_nguoi_dung = BANG_PHAN_LOAI[role_dai_duong.id]["loai"]
        dac_diem = BANG_PHAN_LOAI[role_dai_duong.id]["dac_diem"]
        ten_ca_the_random = random.choice(BANG_PHAN_LOAI[role_dai_duong.id]["danh_sach_ten"])

        ten_hien_thi = after.display_name
        ngay = datetime.datetime.now().strftime("%d/%m/%Y")
        onlyngay = datetime.datetime.now().strftime("%d")
        thu_tu = len(after.guild.members)
        so_ho_chieu = f"{random.randint(0, 999):03d}-{random.randint(0, 999):03d}-{random.randint(0, 999):03d}"

        # Điền thông tin vào form Passport
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
        
        # Hiển thị Avatar
        if after.display_avatar:
            avatar_req = urllib.request.Request(str(after.display_avatar.url), headers={'User-Agent': 'Mozilla/5.0'})
            avatar_img = Image.open(io.BytesIO(urllib.request.urlopen(avatar_req).read())).convert("RGBA")
            SIZE_AV = 182 
            avatar_img = avatar_img.resize((SIZE_AV, SIZE_AV), Image.Resampling.LANCZOS)
            mask = Image.new("L", (SIZE_AV, SIZE_AV), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, SIZE_AV, SIZE_AV), fill=255)
            img.paste(avatar_img, (77, 131), mask)
        
        # Xuất hình ảnh
        with io.BytesIO() as binary:
            img.convert("RGB").save(binary, 'JPEG', quality=95)
            binary.seek(0)
            file_passport = discord.File(binary, filename='passport.jpg')
            
            # --- CẤU HÌNH KÊNH (ID) ---
            ID_KENH_RULE = 1516117766409683075    # < KÊNH RULE
            ID_KENH_TICKET = 1515051548034601020  # < KÊNH HỖ TRỢ
            ID_KENH_ROLE = 1511001081117937755    # < KÊNH VAI TRÒ
            ID_KENH_PROFILE = 1515053474683813918 # < KÊNH THÔNG TIN THÀNH VIÊN
            # Khởi tạo Embed
            embed = discord.Embed(
                title="🌊 HỘ CHIẾU CƯ DÂN ĐẠI DƯƠNG 🐚",
                description=(
                    f"Giữa đêm mưa gió bão bùng, {after.mention} bị cuốn trôi theo dòng hải lưu rơi vào **𝓞𝓬𝓮𝓪𝓷 𝓦𝓪𝓿𝓮** ✨\n\n"
                    f"Good vibes only! Here’s how we keep this place awesome﹒\n"
                    f"⋅‧ ⟡ ‧₊˚┆<#1516117766409683075>\n"
                    f"╰‧₊˚ Ghé qua tham khảo một xíu luật lệ của server\n\n"
                    f"Every star shines differently. Pick your roles and show us your unique light﹒\n"
                    f"⋅‧ ⟡ ⁠‧₊˚┆<#1511001081117937755>\n"
                    f"╰‧₊˚ Lựa chọn nhiều role phù hợp với bạn ở đây nha\n\n"
                    f"We’d love to learn more about you!﹒\n"
                    f"˚₊‧ ⟡ .࿔:･┆<#1515053474683813918>\n"
                    f"╰‧₊˚ Giới thiệu một xíu thông tin về bản thân nha\n\n"
                    f"No voice goes unheard. Whisper your troubles to us﹒\n"
                    f"˚₊‧ ⟡ ⋆.࿔:･┆<#1515051548034601020>\n"
                    f"╰‧₊˚ Tạo ticket khi cần hỗ trợ nè\n\n"
                ),
                color=0x7cd0e6 # <---- Thay đổi mã màu embed
            )
            
            # Thiết lập hình ảnh chính cho Embed lấy từ file đính kèm
            embed.set_image(url="attachment://passport.jpg")
            
            # Gửi đồng thời cả Embed và File ảnh lên kênh chào mừng
            await channel.send(embed=embed, file=file_passport)
            
    except Exception as e: 
        print(f"⚠️ Lỗi khi in Passport: {e}")

# ==========================================
# 5. SỰ KIỆN: TRÒ CHUYỆN VÀ TƯƠNG TÁC
# ==========================================
@client.event
async def on_message(message):
    if message.author == client.user: return
    # ----------------------------------------------------
    # TÍNH NĂNG 1: LỆNH THẢ BIỂN CẢNH BÁO BẪY (.setupbait)
    if message.content == ".setupbait":
        if not message.author.guild_permissions.administrator:
            return 
            
        embed = discord.Embed(
            title="⚠️ **THE ABYSS** ⚠️",
            description=(
                "**WARNING !**\n\n"
                "Kênh này thuần chống spam, nên không nhắn tin vào đây nha mọi người\n\n"
                "Biện pháp này nhằm trục xuất các tài khoản bị hack đi rải link độc hại. Xin hãy cẩn trọng!"
            ),
            color=0xff0000 
        )
        embed.set_image(url="https://i.pinimg.com/736x/c2/48/6f/c2486fce2ffc0d5264c341495443e0fb.jpg") 
        embed.set_footer(text="Kênh này dành để chống spam tin nhắn khi một tài khoản bị hack")
        
        await message.channel.send(embed=embed)
        await message.delete() 
        return

    # TÍNH NĂNG 2: BẪY HẢI TẶC (HONEYPOT AUTO-BAN)
    if message.channel.id == ID_KENH_BAY_HAI_TAC:
        # BẢO MẬT CẤP CAO: Tuyệt đối không ban Admin hoặc các Bot khác
        if message.author.guild_permissions.administrator or message.author.bot:
            return
        
        try:
            await message.delete()
            await message.author.ban(reason="Người dùng nhắn vào kênh no_chat (Nghi ngờ tài khoản bị hack đi spam).",delete_message_days=7
        )
            
            try:
                admin = await client.fetch_user(ID_ADMIN_TOI_CAO)
                await admin.send(f"🚨 **BÁO ĐỘNG ĐỎ KÍCH HOẠT**\nTài khoản **{message.author.name}** (ID: `{message.author.id}`) vừa bị trục xuất vĩnh viễn vì lọt vào bẫy hải tặc!")
            except: pass
            
        except discord.errors.Forbidden:
            print("⚠️ Reze không có quyền Ban người này (Role của Reze nằm dưới Role của người vi phạm).")
        return
    # ----------------------------------------------------
    # TÍNH NĂNG 3: ÂM VANG ĐẠI DƯƠNG (CONFESSION TRONG DM)
    if isinstance(message.channel, discord.DMChannel) and message.content.startswith('.gui'):
        noidung_tam_su = message.content.replace('.gui', '').strip()
        
        if not noidung_tam_su:
            await message.reply("🐚 Bạn quên gửi gắm âm vang rồi! Hãy dùng cú pháp: `.gui [nội dung tâm sự]` nhé.")
            return

        kenh_tam_su = client.get_channel(ID_KENH_CFS)
        if kenh_tam_su is None:
            await message.reply("⚠️ Sóng đánh trôi mất kênh tâm sự rồi. Bạn báo quản trị viên kiểm tra lại ID kênh nhé!")
            return

        kho = doc_tri_nho()
        so_cfs = kho.get("cfs_count", 0) + 1
        kho["cfs_count"] = so_cfs
        ghi_tri_nho(kho)

        # Cập nhật lại tên Embed trong DM cho khớp với giao diện mới
        embed = discord.Embed(
            title=f"𓆡⋆.°🐚⋆ Âm vang #{so_cfs} đến từ đại dương ˖°🫧",
            description=f"*{noidung_tam_su}*",
            color=0x7cd0e6,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="🐟⋆｡𖦹° Gửi ẩn danh qua Reze | Dùng lệnh /cfs hoặc .gui nhé 🫧⋆.ೃ࿔*:･")

        try:
            await kenh_tam_su.send(embed=embed, view=CfsView())
            await message.reply(f"𓆝⋆.˚ Âm vang **#{so_cfs}** của bạn đã được lan tỏa khắp đại dương, hãy chờ hồi đáp nhé.ೃ࿔*")
            # --- TÍNH NĂNG MỚI: BÁO CÁO MẬT CHO ADMIN TỐI CAO ---
            try:
                admin = await client.fetch_user(ID_ADMIN_TOI_CAO)
                await admin.send(f"🕵️ **BÁO CÁO MẬT - Âm Vang #{so_cfs}**\n👤 Gửi qua tin nhắn riêng (.gui)\nTác giả: **{message.author.name}** (ID: `{message.author.id}`)")
            except:
                pass
            # ---------------------------------------------------
        except Exception as e:
            await message.reply(f"⚠️ Có lỗi khi lan tỏa âm vang: {e}")
        return
        
    # Tính năng gọi Trạm Thu Thập Âm Vang (Chỉ Admin dùng được)
    if message.content == ".setupcfs":
        if not message.author.guild_permissions.administrator:
            return 
            
        embed = discord.Embed(
            title="⋅˚₊‧🐚 LAN TỎA TIẾNG VỌNG ĐẾN KHẮP ĐẠI DƯƠNGଳ⋆.࿔*",
            description=(
                "⋆. 𐙚˚࿔ *Những tâm tư thầm kín khó nói >.<* 𝜗𝜚˚⋆ \n"
                "⋆. 𐙚˚࿔ *Thích một ai đó nhưng hong biếc phải làm sao* 𝜗𝜚˚⋆\n"
                "⋆. 𐙚˚࿔ *Muốn chia sẻ đời sống một cách ẩn danh* 𝜗𝜚˚⋆\n\n"
                ".ೃ࿔*･ **Bạn đến đúng chỗ rồi, hãy ấn nút bên dưới để gửi ngay tâm thư thầm kín của bạn nhé 🩵**₊˚\n"
            ),
            color=0x7cd0e6
        )
        # --- THÊM HÌNH ẢNH TRANG TRÍ VÀO ĐÂY VÀ THAY LINK ẢNH CỦA BẠN VÀO ---
        # Cách 1: Nếu muốn dùng Banner lớn nằm ở phía dưới đáy Embed:
        embed.set_image(url="https://i.pinimg.com/736x/58/75/b1/5875b163b15f92ec3ba41efde14cd3d1.jpg")
        embed.set_footer(text="⊹˖𓇼 ⋆｡˚ Tâm thư của bạn đảm bảo được gửi ẩn danh 100% °‧*:･𓆜⋆˚࿔⊹ ˖")        
        await message.channel.send(embed=embed, view=SetupCfsView())
        await message.delete() 
        return
    #---------------------------------------------------
    # Tính năng gọi Bảng Hướng Dẫn Lập ĐỘI (Chỉ Admin dùng được)
    if message.content == ".setuplapdoi":
        if not message.author.guild_permissions.administrator:
            return 
            
        embed = discord.Embed(
            title="⋆.°・LẬP TEAM CHIẾN GAME・˖°🪼",
            description=(
                "⋆. 𐙚 ˚ Bạn cần tìm một vài đồng đội leo rank cực cháy nhưng ngại tag?\n\n"
                "⋆. 𐙚 ˚ Hãy đăng một bảng chiêu mộ để bất cứ ai cũng có thể tham gia nhé ~\n\n"
                "⋆. 𐙚 ˚ Cách thức đăng bảng chiêu mộ: gõ lệnh **/lapdoi** và bổ sung thông tin cần thiết\n"
                "⋆˙ ⟡ **ten_game:** Tên trò chơi (Ví dụ: TFT, Valorant, Liên Minh...)\n"
                "⋆˙ ⟡ **so_luong:** Số người tối đa của tổ đội *(Ví dụ: 5)\n"
                "⋆˙ ⟡ **bac_rank:** Bậc rank mong muốn (Ví dụ: Lục Bảo, Kim Cương...)\n"
                "⋆˙ ⟡ **noi_dung:** Mô tả về trạng thái team (Ví dụ: try hard, vui là chính, chill chill...)\n\n"
                "﹌﹌﹌﹌﹌﹌﹌﹌﹌\n"
                "🛸 Tính năng từ bảng chiêu mộ:\n"
                "• Bảng chiêu mộ sẽ tự động hiển thị và cập nhật liên kết phòng Voice của Đội trưởng.\n"
                "• Thành viên chỉ cần ấn nút **Tham gia**, nếu đang ngồi sẵn ở một phòng Voice chờ bất kỳ, Reze sẽ lập tức 'bế' thẳng vào phòng của Đội trưởng ngay lập tức"
            ),
            color=0x7cd0e6
        )
        
        # Tui có chuẩn bị sẵn một link ảnh banner pixel game đại dương khá xinh, sếp có thể đổi link ảnh khác tùy thích nha
        embed.set_image(url="https://i.pinimg.com/736x/6f/f7/06/6ff7065d1272a10929111e3c27f9f5fd.jpg")
        embed.set_footer(text="⊹˖𓇼 ⋆｡˚ Lập đội để mời thêm mọi người chơi cùng cho vui nha °‧*:･𓆜⋆˚࿔⊹ ˖")
        
        await message.channel.send(embed=embed)
        await message.delete() # Xóa dòng lệnh .setuplapdoi của bạn đi cho sạch kênh
        return
    # ----------------------------------------------------

    # Tính năng test thủ công Passport (Đã cập nhật logic mới)
    if message.content == ".testwelcome":
        # Tạo một đối tượng giả định trạng thái cũ (chưa có role)
        class FakeMember:
            roles = []
        before = FakeMember()
        # Chạy sự kiện update bằng cách giả định sự chênh lệch role
        await on_member_update(before, message.author)
        return

    # Tính năng dạy học bot
    if message.content.startswith('.r học:'):
        noidung_hoc = message.content.replace('.r học:', '').split('=')
        if len(noidung_hoc) == 2:
            kho = doc_tri_nho()
            kho[noidung_hoc[0].strip().lower()] = noidung_hoc[1].strip()
            ghi_tri_nho(kho)
            await message.reply(f"✅ Mình đã lưu vào sổ tay đại dương: **{noidung_hoc[0].strip()}** = {noidung_hoc[1].strip()}")
        else:
            await message.reply("⚠️ Sai cú pháp rồi! Hãy dùng: `.r học: [Từ khóa] = [Ý nghĩa]` nhé!")
        return

    # Tính năng trò chuyện & Hỏi thời tiết
    if message.content.startswith('.p'):
        user_question = message.content.replace('.p', '').strip()
        user_id = message.author.id
        
        if not user_question:
            await message.reply("Cậu hãy nhập câu hỏi để mình biết cậu cần gì nhé 🐚")
            return
            
        if user_id not in tri_nho_nguoi_dung: tri_nho_nguoi_dung[user_id] = model.start_chat(history=[])
        
        du_lieu_thoi_tiet = ""
        if "thời tiết" in user_question.lower():
            try:
                cac_tu_thua = ["dự báo", "thời tiết", "hôm nay", "ngày mai", "hiện tại", "tại", "ở", "khu vực", "thành phố", "tỉnh", "như thế nào", "ra sao", "?", "có mưa không", "bao nhiêu độ"]
                chuoi_dia_diem = user_question.lower()
                for tu in cac_tu_thua: chuoi_dia_diem = chuoi_dia_diem.replace(tu, "")
                thanh_pho = chuoi_dia_diem.strip().replace(" ", "_")
                
                if thanh_pho:
                    url = urllib.parse.quote(f"https://wttr.in/{thanh_pho}?format=3", safe=":/=?&")
                    thoi_tiet = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=5).read().decode().strip()
                    du_lieu_thoi_tiet = f"\n[DỮ LIỆU THỰC TẾ LẤY TỪ WTTR.IN]: Thời tiết tại {thanh_pho.replace('_', ' ')} là: {thoi_tiet}"
            except Exception as e: print(f"Lỗi lấy thời tiết: {e}")

        kien_thuc = "\n".join([f"- {k}: {v}" for k, v in doc_tri_nho().items()])
        prompt = f"[HƯỚNG DẪN ẨN]: Ngày hôm nay là {datetime.datetime.now().strftime('%d/%m/%Y')}. {du_lieu_thoi_tiet}\n[TỪ ĐIỂN SERVER]: {kien_thuc}\n\n[CÂU HỎI TỪ NGƯỜI DÙNG]: {user_question}"
        
        try:
            async with message.channel.typing():
                response = await tri_nho_nguoi_dung[user_id].send_message_async(prompt)
                await message.reply(response.text)
        except Exception as e:
            await message.reply(f"⚠️ Sóng hơi yếu nên mình gặp trục trặc một chút: {e}")

# Kích hoạt trạm gác
client.run('MTUxNzQ4MjU2Mzc0NzE4NDg0MA.GETwXD.-hMAe1ikMmDlo-ebl3Xo-J-Z6d_l7csLbgWJbA')
