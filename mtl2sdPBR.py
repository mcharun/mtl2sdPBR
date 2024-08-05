#coding:utf-8
import re
#mtlファイル解析関数の定義
def parse_mtl_file(file_path):
    # マテリアルごとのパラメーターを格納する辞書のリスト
    materials = []
    current_material = None

    # パラメーター名のリスト
    param_names = [
        'newmtl', 'Kd', 'Ke', 'Ni','Pr', 'Pm', 'Ps', 'Pc', 'Pcr','aniso', 'anisor','map_Kd', 'map_Pr', 'map_Pm','map_d','map_Bump','map_Ke']
    
    # 正規表現パターンの作成
    param_pattern = re.compile(r'^(' + '|'.join(param_names) + r')\s+(.*)$')

    # MTLファイルの解析
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            match = param_pattern.match(line)
            if match:
                param_name, param_value = match.groups()
                if param_name == 'newmtl':
                    if current_material:
                        materials.append(current_material)
                    current_material = {'name': param_value, 'params': {}}
                elif current_material:
                    current_material['params'][param_name] = param_value

        if current_material:
            materials.append(current_material)

    return materials

# ファイルの入力
mtl_file_path = input("mtl file path:")
fx_file_path= input("fx file path:")

# MTLファイルを解析してマテリアルごとのパラメーターを取得
parsed_materials = parse_mtl_file(mtl_file_path)

# ファイルの書き込み  
for materialnum in range(len(parsed_materials)):
  materialname=parsed_materials[materialnum]['name']

  # マテリアルごとにファイルを作成
  with open (fx_file_path+materialname.replace('/','_')+'.fx' ,'w') as fxfile:
    paramlist=parsed_materials[materialnum]['params']
    #書き込み用にパラメーター名リストを再定義  
    param_names = ['Kd', 'Ke', 'Ni','Pr', 'Pm', 'Ps', 'Pc', 'Pcr','aniso', 'anisor']
    tex_names=['map_Kd', 'map_Pr', 'map_Pm','map_d','map_Bump','map_Ke']
    #最初のおまじないを書き込み
    fxfile.write('#define SDPBR_MATERIAL_VER 100\n#include "../../shader/sdPBRMaterialHead.fxsub"\n\nvoid SetMaterialParam(inout Material m, float3 n,float3 l, float3 Eye, float2 uv)\n{\n')
    #テクスチャ以外のパラメーターを書き込み
    for paramnum in range(10):
        try:
            param_name=param_names[paramnum]
            param=paramlist[param_name]
            #sdPBRのパラメーターの書式リスト
            sdPBR_param_list=[
            'm.baseColor=float3('+param.replace(' ',',')+')','m.emissiveColor=float3('+param.replace(' ',',')+')','m.specular=IORtoSpecular('+param+')',
            'm.roughness='+param,'m.metallic='+param,'m.sheen='+param,'m.clearcoat='+param,'m.clearcoatGloss='+param,
            'm.anisotropic='+param,'m.anisoAngleX='+param
            ]
            fxfile.write(' '+sdPBR_param_list[paramnum]+';\n')
        #mtlファイルで未定義のパラメータは飛ばす
        except KeyError:
            print('',end='')
    
    #ノーマルマップだけ書式が違うので別で処理        
    try:
        normaldata=paramlist['map_Bump']
        normallist=normaldata.split()
        if len(normallist)!=1:
                fxfile.write(' '+'m.normalScale='+normallist[1]+';\n')
    except KeyError:
        print('',end='')
        normallist=param
    fxfile.write('}\n\n')
    #テクスチャの書き込み
    for texnum in range(6):
        try:
            param_name=tex_names[texnum]
            param=paramlist[param_name]
            #sdPBRのテクスチャ書式のリスト
            sdPBR_tex_list=[
            '#define BASECOLOR_FROM BASECOLOR_FROM_FILE\n#define BASECOLOR_FILE \"'+param+'\"',
            '#define ROUGHNESS_FROM ROUGHNESS_FROM_FILE\n#define ROUGHNESS_FILE \"'+param+'\"',
            '#define METALLIC_FROM METALLIC_FROM_FILE\n#define METALIC_FILE \"'+param+'\"',
            '#define MASK_FROM MASK_FROM_FILE\n#define MASK_FILE \"'+param+'\"',
            '#define NORMAL_FROM NORMAL_FROM_FILE\n#define NORMAL_FILE \"'+normallist[-1]+'\"',
            '#define EMISSIVE_FROM EMISSIVE_FROM_FILE\n#define EMISSIVE_FILE \"'+param+'\"',
            ]
            fxfile.write(sdPBR_tex_list[texnum]+'\n')
        except KeyError:
            print('',end='')
    fxfile.write('\n\n#include "../../shader/sdPBRMaterialTail.fxsub"')

#終わり
end=input('end')

