import pandas as pd
import os
import json

def audit_data():
    processed_dir = 'data/processed'
    contracts_path = os.path.join(processed_dir, 'contracts.csv')
    
    if not os.path.exists(contracts_path):
        print(f"Error: {contracts_path} not found. Run process_data.py first.")
        return

    df = pd.read_csv(contracts_path)
    df['fecha_adjudicacion'] = pd.to_datetime(df['fecha_adjudicacion'], errors='coerce')

    anomalies = []

    def add_anomaly(row, tipo, detalle):
        anomalies.append({
            'source_file': row.get('source_file', 'unknown'),
            'expediente': row.get('expediente', 'N/A'),
            'adjudicatario': row['adjudicatario'],
            'tipo_anomalia': tipo,
            'detalle': detalle,
            'contenido_original': row.get('raw_row', '')
        })

    # 1. CIF Issues (Missing or Invalid)
    no_cif = df[df['cif'].isna() | (df['cif'] == '')]
    for _, row in no_cif.iterrows():
        add_anomaly(row, 'CIF Faltante', 'No se pudo encontrar ningún código de identificación')

    invalid_cif = df[(~df['cif'].isna()) & (df['cif'] != '') & (df['check_cif'] == False)]
    for _, row in invalid_cif.iterrows():
        add_anomaly(row, 'CIF Inválido', f"El código '{row['cif']}' no pasa el algoritmo de validación")

    # 2. Outlier Dates
    missing_dates = df[df['fecha_adjudicacion'].isna()]
    for _, row in missing_dates.iterrows():
        add_anomaly(row, 'Fecha Inválida/Faltante', 'La fecha es nula o estaba fuera del rango 2020-2026')

    # 3. Anomalous Amounts
    high_amounts = df[df['importe'] > 50000]
    for _, row in high_amounts.iterrows():
        add_anomaly(row, 'Importe Elevado', f"Importe de {row['importe']}€ supera el umbral común de contratos menores")

    zero_amounts = df[df['importe'] <= 0]
    for _, row in zero_amounts.iterrows():
        add_anomaly(row, 'Importe Cero/Negativo', "El importe registrado es 0 o menor")

    # 4. Missing Object
    missing_object = df[df['objeto'].isna() | (df['objeto'] == '')]
    for _, row in missing_object.iterrows():
        add_anomaly(row, 'Objeto Faltante', "No hay descripción del objeto del contrato")

    # Generate Report
    audit_df = pd.DataFrame(anomalies)
    output_path = os.path.join(processed_dir, 'audit_report.csv')
    
    if not audit_df.empty:
        cols = ['source_file', 'expediente', 'adjudicatario', 'tipo_anomalia', 'detalle', 'contenido_original']
        audit_df = audit_df[cols]
    
    audit_df.to_csv(output_path, index=False)

    print(f"Audit complete.")
    print(f"  - Total records checked: {len(df)}")
    print(f"  - Anomalies found: {len(audit_df)}")
    print(f"  - Report saved to: {output_path}")

    # Summary Statistics
    summary = {
        'total_checked': len(df),
        'total_anomalies': len(audit_df),
        'by_type': audit_df['tipo_anomalia'].value_counts().to_dict() if not audit_df.empty else {}
    }
    
    with open(os.path.join(processed_dir, 'audit_summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    audit_data()

