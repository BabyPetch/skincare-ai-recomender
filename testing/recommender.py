# -*- coding: utf-8 -*-
import sys
import io
import pandas as pd
from pathlib import Path

# ตั้งค่า encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_FILE = Path('C:/Users/Petch/Desktop/Projectskin/skincare-ai-recomender/data/Data_Collection_ASA - data.csv')

class InteractiveSkinCareAnalyzer:
    """ระบบวิเคราะห์ผิวและแนะนำผลิตภัณฑ์แบบโต้ตอบ"""
    
    def __init__(self):
        self.df = None
        self.user_profile = {}
        self.load_data()
    
    def load_data(self):
        """โหลดข้อมูล"""
        try:
            self.df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
            print(f"✓ โหลดข้อมูลสำเร็จ: {len(self.df)} ผลิตภัณฑ์\n")
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            sys.exit(1)
    
    def clear_screen(self):
        """ล้างหน้าจอ (เสมือน)"""
        print("\n" * 2)
    
    def print_header(self, text):
        """พิมพ์หัวข้อ"""
        print("\n" + "=" * 80)
        print(f"✨ {text}")
        print("=" * 80)
    
    def get_input(self, prompt, options=None, allow_skip=False):
        """รับ input จากผู้ใช้"""
        while True:
            if options:
                print(f"\n{prompt}")
                for i, option in enumerate(options, 1):
                    print(f"  {i}. {option}")
                if allow_skip:
                    print(f"  0. ข้าม")
                
                choice = input("\n👉 เลือก (ใส่หมายเลข): ").strip()
                
                if allow_skip and choice == '0':
                    return None
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        return options[idx]
                    else:
                        print("❌ กรุณาเลือกหมายเลขที่ถูกต้อง")
                except ValueError:
                    print("❌ กรุณาใส่ตัวเลข")
            else:
                response = input(f"\n{prompt}: ").strip()
                if response or not allow_skip:
                    return response
                return None
    
    def analyze_skin_type(self):
        """วิเคราะห์ประเภทผิว"""
        self.print_header("ขั้นตอนที่ 1: วิเคราะห์ประเภทผิว")
        
        print("\n🔍 ตอบคำถามเพื่อวิเคราะห์ประเภทผิวของคุณ")
        
        # คำถามที่ 1: หน้ามันหรือไม่
        q1 = self.get_input(
            "หลังล้างหน้า 2-3 ชั่วโมง ผิวหน้าของคุณรู้สึกอย่างไร?",
            ["มันมาก (บริเวณ T-zone และทั้งหน้า)",
             "มันปานกลาง (เฉพาะบริเวณ T-zone)",
             "แห้งตึง ไม่ค่อยมีความมัน",
             "ปกติ สบาย ไม่แห้งไม่มัน"]
        )
        
        # คำถามที่ 2: ปัญหาผิว
        q2 = self.get_input(
            "คุณมีปัญหาผิวอะไรบ้าง? (เลือกที่ใกล้เคียงที่สุด)",
            ["สิว หัวดำ รูขุมขนกว้าง",
             "ผิวแห้ง ลอก คัน",
             "ผิวแพ้ง่าย แดง ระคายเคือง",
             "ไม่มีปัญหาเป็นพิเศษ"]
        )
        
        # คำถามที่ 3: สภาพแวดล้อม
        q3 = self.get_input(
            "คุณอยู่ในสภาพแวดล้อมแบบไหนเป็นส่วนใหญ่?",
            ["ที่แจ้ง ร้อน แดดจัด",
             "ห้องแอร์ ออฟฟิศ",
             "บ้าน ปกติทั่วไป"]
        )
        
        # วิเคราะห์ผล
        skin_type = self._determine_skin_type(q1, q2, q3)
        
        self.user_profile['skin_type'] = skin_type
        self.user_profile['concerns'] = self._extract_concerns(q1, q2)
        
        print(f"\n✅ ผลการวิเคราะห์:")
        print(f"   🧴 ประเภทผิว: {self._translate_skin_type(skin_type)}")
        print(f"   ⚠️  ปัญหาที่ควรดูแล: {', '.join(self.user_profile['concerns'])}")
    
    def _determine_skin_type(self, q1, q2, q3):
        """กำหนดประเภทผิวจากคำตอบ"""
        if "มันมาก" in q1:
            return "oily"
        elif "มันปานกลาง" in q1:
            return "combination"
        elif "แห้งตึง" in q1:
            return "dry"
        elif "ผิวแพ้ง่าย" in q2:
            return "sensitive"
        else:
            return "normal"
    
    def _translate_skin_type(self, skin_type):
        """แปลประเภทผิวเป็นภาษาไทย"""
        translations = {
            'oily': 'ผิวมัน',
            'dry': 'ผิวแห้ง',
            'normal': 'ผิวปกติ',
            'combination': 'ผิวผสม',
            'sensitive': 'ผิวแพ้ง่าย'
        }
        return translations.get(skin_type, skin_type)
    
    def _extract_concerns(self, q1, q2):
        """สรุปปัญหาผิวจากคำตอบ"""
        concerns = []
        if "สิว" in q2:
            concerns.extend(['สิว', 'ควบคุมความมัน', 'รูขุมขน'])
        if "แห้ง" in q2 or "แห้ง" in q1:
            concerns.extend(['ผิวแห้ง', 'เสริมความชุ่มชื้น'])
        if "แพ้ง่าย" in q2:
            concerns.extend(['ผิวระคายเคือง', 'ผิวแพ้ง่าย'])
        if not concerns:
            concerns.append('ดูแลทั่วไป')
        return concerns
    
    def get_preferences(self):
        """รับข้อมูลความต้องการเพิ่มเติม"""
        self.print_header("ขั้นตอนที่ 2: ความต้องการของคุณ")
        
        # ประเภทผลิตภัณฑ์ที่ต้องการ
        product_types = self.get_input(
            "คุณกำลังหาผลิตภัณฑ์ประเภทไหน?",
            ["Cleanser (ล้างหน้า)",
             "Moisturizer (ครีมบำรุง)",
             "Serum (เซรั่ม)",
             "Sunscreen (กันแดด)",
             "ทุกประเภท"],
            allow_skip=False
        )
        
        if "ทุกประเภท" not in product_types:
            self.user_profile['product_type'] = product_types.split()[0]
        else:
            self.user_profile['product_type'] = None
        
        # งบประมาณ
        budget = self.get_input(
            "งบประมาณของคุณ?",
            ["ไม่เกิน 300 บาท",
             "300-700 บาท",
             "700-1500 บาท",
             "มากกว่า 1500 บาท",
             "ไม่จำกัด"],
            allow_skip=False
        )
        
        if "ไม่เกิน 300" in budget:
            self.user_profile['max_price'] = 300
        elif "300-700" in budget:
            self.user_profile['max_price'] = 700
        elif "700-1500" in budget:
            self.user_profile['max_price'] = 1500
        elif "มากกว่า 1500" in budget:
            self.user_profile['max_price'] = 5000
        else:
            self.user_profile['max_price'] = None
        
        # ยี่ห้อที่ชอบ (ถ้ามี)
        brands_available = self.df['brand'].unique().tolist()[:10]
        print(f"\n💼 ยี่ห้อที่มีในระบบ (ตัวอย่าง): {', '.join(brands_available[:5])}, ...")
        
        preferred_brand = input("\n👉 คุณชอบยี่ห้อไหนเป็นพิเศษไหม? (พิมพ์ชื่อ หรือ Enter เพื่อข้าม): ").strip()
        if preferred_brand:
            self.user_profile['brand'] = preferred_brand
    
    def recommend(self):
        """แนะนำผลิตภัณฑ์ตามข้อมูลที่วิเคราะห์"""
        self.print_header("ขั้นตอนที่ 3: ผลการแนะนำ")
        
        print("\n🔄 กำลังวิเคราะห์และจัดอันดับผลิตภัณฑ์...")
        
        # กรองตามประเภทผิว
        df_filtered = self.df[
            self.df['skintype'].fillna('').str.contains(
                self.user_profile['skin_type'], case=False, na=False
            )
        ].copy()
        
        # กรองตามประเภทผลิตภัณฑ์
        if self.user_profile.get('product_type'):
            df_filtered = df_filtered[
                df_filtered['type_of_product'].fillna('').str.contains(
                    self.user_profile['product_type'], case=False, na=False
                )
            ]
        
        # กรองตามราคา
        if self.user_profile.get('max_price'):
            df_filtered = df_filtered[
                df_filtered['price (bath)'] <= self.user_profile['max_price']
            ]
        
        # กรองตามยี่ห้อ (ถ้ามี)
        if self.user_profile.get('brand'):
            df_filtered = df_filtered[
                df_filtered['brand'].fillna('').str.contains(
                    self.user_profile['brand'], case=False, na=False
                )
            ]
        
        if len(df_filtered) == 0:
            print("\n❌ ไม่พบผลิตภัณฑ์ที่ตรงกับเงื่อนไข")
            print("💡 ลองปรับเงื่อนไข เช่น เพิ่มงบประมาณ หรือเปลี่ยนประเภทผลิตภัณฑ์")
            return
        
        # คำนวณคะแนน
        df_filtered = self._calculate_scores(df_filtered)
        
        # เรียงตามคะแนน
        df_filtered = df_filtered.sort_values('total_score', ascending=False)
        
        # แสดงผลลัพธ์
        self._display_results(df_filtered.head(10))
        
        # บันทึกผลลัพธ์
        output_file = f'recommended_{self.user_profile["skin_type"]}.csv'
        df_filtered.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 บันทึกผลลัพธ์ทั้งหมดไว้ที่: {output_file}")
    
    def _calculate_scores(self, df):
        """คำนวณคะแนนความเหมาะสม"""
        df['total_score'] = 0
        
        # 1. คะแนนจากราคา (30 คะแนน - ยิ่งถูกยิ่งดี)
        max_p = df['price (bath)'].max()
        min_p = df['price (bath)'].min()
        if max_p > min_p:
            df['price_score'] = (1 - (df['price (bath)'] - min_p) / (max_p - min_p)) * 30
        else:
            df['price_score'] = 30
        df['total_score'] += df['price_score']
        
        # 2. คะแนนจากความตรงกับประเภทผิว (40 คะแนน)
        skin_type = self.user_profile['skin_type']
        df['skin_match_score'] = df['skintype'].apply(
            lambda x: 40 if str(x).lower() == skin_type.lower() 
                     else 20 if skin_type.lower() in str(x).lower() 
                     else 0
        )
        df['total_score'] += df['skin_match_score']
        
        # 3. คะแนนจากคำที่เกี่ยวข้องกับปัญหาผิว (30 คะแนน)
        concerns = self.user_profile.get('concerns', [])
        df['concern_score'] = 0
        for concern in concerns:
            df['concern_score'] += df['คุณสมบัติ(จากactive ingredients)'].fillna('').str.contains(
                concern, case=False
            ).astype(int) * (30 / len(concerns))
        df['total_score'] += df['concern_score']
        
        return df
    
    def _display_results(self, df):
        """แสดงผลลัพธ์การแนะนำ"""
        print("\n" + "=" * 90)
        print("🏆 TOP 10 ผลิตภัณฑ์ที่แนะนำสำหรับคุณ")
        print("=" * 90)
        
        for rank, (idx, row) in enumerate(df.iterrows(), 1):
            print(f"\n{'🥇' if rank == 1 else '🥈' if rank == 2 else '🥉' if rank == 3 else '🔸'} อันดับ {rank}")
            print(f"   📦 {row['name']}")
            print(f"   💼 แบรนด์: {row['brand']}")
            print(f"   🧴 ประเภท: {row['type_of_product']}")
            print(f"   ✅ ผิว: {row['skintype']}")
            print(f"   💰 ราคา: {row['price (bath)']:.0f} บาท")
            print(f"   ⭐ คะแนนความเหมาะสม: {row['total_score']:.1f}/100")
            
            if pd.notna(row['active ingredients']):
                ingredients = str(row['active ingredients'])[:80]
                print(f"   ✨ ส่วนผสมสำคัญ: {ingredients}...")
            
            if pd.notna(row['คุณสมบัติ(จากactive ingredients)']):
                props = str(row['คุณสมบัติ(จากactive ingredients)'])[:80]
                print(f"   💫 คุณสมบัติ: {props}...")
        
        print("\n" + "=" * 90)
        print(f"💡 พบผลิตภัณฑ์ที่เหมาะสมทั้งหมด {len(df)} รายการ")
        print("=" * 90)
    
    def show_summary(self):
        """แสดงสรุปข้อมูลผู้ใช้"""
        self.print_header("สรุปข้อมูลของคุณ")
        
        print(f"\n🧴 ประเภทผิว: {self._translate_skin_type(self.user_profile['skin_type'])}")
        print(f"⚠️  ปัญหาที่ควรดูแล: {', '.join(self.user_profile['concerns'])}")
        
        if self.user_profile.get('product_type'):
            print(f"📦 ผลิตภัณฑ์ที่ต้องการ: {self.user_profile['product_type']}")
        
        if self.user_profile.get('max_price'):
            print(f"💰 งบประมาณ: ไม่เกิน {self.user_profile['max_price']} บาท")
        
        if self.user_profile.get('brand'):
            print(f"💼 ยี่ห้อที่ชอบ: {self.user_profile['brand']}")
    
    def run(self):
        """เริ่มการทำงานของระบบ"""
        print("\n" + "=" * 90)
        print("🌟 ยินดีต้อนรับสู่ระบบแนะนำผลิตภัณฑ์ดูแลผิวอัจฉริยะ")
        print("=" * 90)
        print("\n💡 ระบบจะวิเคราะห์ผิวของคุณและแนะนำผลิตภัณฑ์ที่เหมาะสมที่สุด")
        
        input("\n👉 กด Enter เพื่อเริ่มต้น...")
        
        # ขั้นตอนที่ 1: วิเคราะห์ผิว
        self.analyze_skin_type()
        
        # ขั้นตอนที่ 2: รับความต้องการ
        self.get_preferences()
        
        # สรุปข้อมูล
        self.show_summary()
        
        # ยืนยันก่อนแนะนำ
        confirm = input("\n👉 ดำเนินการต่อเพื่อรับคำแนะนำ? (Enter เพื่อดำเนินการต่อ): ")
        
        # ขั้นตอนที่ 3: แนะนำผลิตภัณฑ์
        self.recommend()
        
        print("\n✨ ขอบคุณที่ใช้บริการ!")
        print("=" * 90)

# ========================
# เริ่มการทำงาน
# ========================
if __name__ == '__main__':
    analyzer = InteractiveSkinCareAnalyzer()
    analyzer.run()