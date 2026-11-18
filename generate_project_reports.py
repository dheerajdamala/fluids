"""
Academic Project Report Generator
Compiles separate, comprehensive, publication-quality academic project reports for:
1. Smart Maze-Solving Robot (AI with Python Course Project)
2. Laminar Water Pipe Flow CFD Simulation (Fluid Mechanics Course Assignment)

Uses headless Microsoft Edge to render pixel-perfect vector A4 PDFs.
"""

import os
import sys
import base64
import subprocess
import shutil

def img_to_b64(path):
    if not os.path.exists(path):
        print(f"Warning: Image not found at {path}")
        return ""
    with open(path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode('utf-8')}"

def find_edge_binary():
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("Could not find Edge or Chrome executable for PDF compilation.")

def compile_html_to_pdf(html_content, output_pdf_path, temp_html_path):
    browser_exe = find_edge_binary()
    
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    cmd = [
        browser_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={output_pdf_path}",
        temp_html_path
    ]
    
    print(f"Compiling PDF -> {output_pdf_path}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(temp_html_path):
        try:
            os.remove(temp_html_path)
        except Exception:
            pass
            
    if os.path.exists(output_pdf_path):
        size = os.path.getsize(output_pdf_path)
        print(f"Generated successfully: {output_pdf_path} ({size:,} bytes)")
        return True
    else:
        print(f"Compilation failed for {output_pdf_path}: {res.stderr}")
        return False

def build_ai_report():
    print("\n--- Generating AI with Python Report ---")
    template_path = r"c:\Users\dheer\Desktop\kani\reports_templates\ai_report_template.html"
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    ai_img_path = r"c:\Users\dheer\Desktop\ai-maze-robot\ai with python\benchmark_comparison.png"
    ai_img_b64 = img_to_b64(ai_img_path)
    
    html = html.replace("{{AI_BENCHMARK_IMG}}", ai_img_b64)
    
    desktop_pdf = r"c:\Users\dheer\Desktop\AI_with_Python_Maze_Robot_Project_Report.pdf"
    repo_pdf = r"c:\Users\dheer\Desktop\ai-maze-robot\AI_with_Python_Maze_Robot_Project_Report.pdf"
    temp_html = r"c:\Users\dheer\Desktop\kani\_temp_ai_report.html"
    
    success = compile_html_to_pdf(html, desktop_pdf, temp_html)
    if success:
        shutil.copyfile(desktop_pdf, repo_pdf)
        print(f"Copied to AI Repo: {repo_pdf}")

def build_fluids_report():
    print("\n--- Generating Fluid Mechanics CFD Report ---")
    template_path = r"c:\Users\dheer\Desktop\kani\reports_templates\fluids_report_template.html"
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    results_dir = r"c:\Users\dheer\Desktop\kani\fluids\results"
    b64_contour = img_to_b64(os.path.join(results_dir, "velocity_contour.png"))
    b64_profiles = img_to_b64(os.path.join(results_dir, "velocity_profiles.png"))
    b64_centerline = img_to_b64(os.path.join(results_dir, "centerline_velocity.png"))
    b64_pressure = img_to_b64(os.path.join(results_dir, "pressure_drop.png"))
    b64_shear = img_to_b64(os.path.join(results_dir, "wall_shear_stress.png"))
    
    html = html.replace("{{CONTOUR_IMG}}", b64_contour)
    html = html.replace("{{PROFILES_IMG}}", b64_profiles)
    html = html.replace("{{CENTERLINE_IMG}}", b64_centerline)
    html = html.replace("{{PRESSURE_IMG}}", b64_pressure)
    html = html.replace("{{SHEAR_IMG}}", b64_shear)
    
    desktop_pdf = r"c:\Users\dheer\Desktop\Fluid_Mechanics_Pipe_Flow_CFD_Report.pdf"
    repo_pdf = r"c:\Users\dheer\Desktop\kani\Fluid_Mechanics_Pipe_Flow_CFD_Report.pdf"
    temp_html = r"c:\Users\dheer\Desktop\kani\_temp_fluids_report.html"
    
    success = compile_html_to_pdf(html, desktop_pdf, temp_html)
    if success:
        shutil.copyfile(desktop_pdf, repo_pdf)
        print(f"Copied to Fluids Repo: {repo_pdf}")

def main():
    build_ai_report()
    build_fluids_report()
    print("\nAll reports compiled successfully!")

if __name__ == "__main__":
    main()
