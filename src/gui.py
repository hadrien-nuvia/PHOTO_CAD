"""GUI application for orthophoto to DXF conversion using tkinter."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading

# Support both relative imports (when used as module) and absolute imports (when run directly)
try:
    from .convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf
except ImportError:
    try:
        from convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf
    except ImportError:
        from src.convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf


class OrthoPhotoConverterGUI:
    """GUI application for converting orthophotos to DXF."""

    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Orthophoto to DXF Converter")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.geojson_path = tk.StringVar()
        self.snap_angle = tk.IntVar(value=15)
        self.low_threshold = tk.IntVar(value=50)
        self.high_threshold = tk.IntVar(value=150)
        self.line_threshold = tk.IntVar(value=100)
        self.min_line_length = tk.IntVar(value=100)
        self.max_line_gap = tk.IntVar(value=10)
        self.enable_geojson = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # File selection section
        files_frame = ttk.LabelFrame(main_frame, text="Files", padding="10")
        files_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Input file
        ttk.Label(files_frame, text="Input Image:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(files_frame, textvariable=self.input_path, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(files_frame, text="Browse...", command=self.browse_input).grid(
            row=0, column=2, padx=5
        )

        # Output DXF file
        ttk.Label(files_frame, text="Output DXF:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(files_frame, textvariable=self.output_path, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(files_frame, text="Browse...", command=self.browse_output).grid(
            row=1, column=2, padx=5
        )

        # GeoJSON output (optional)
        ttk.Checkbutton(files_frame, text="Export GeoJSON", variable=self.enable_geojson).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(files_frame, textvariable=self.geojson_path, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(files_frame, text="Browse...", command=self.browse_geojson).grid(
            row=2, column=2, padx=5
        )

        files_frame.columnconfigure(1, weight=1)

        # Parameters section
        params_frame = ttk.LabelFrame(main_frame, text="Parameters", padding="10")
        params_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        row = 0
        # Snap angle
        ttk.Label(params_frame, text="Snap Angle (degrees):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Spinbox(
            params_frame,
            from_=1,
            to=90,
            textvariable=self.snap_angle,
            width=10,
        ).grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="Angle increment for snapping").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )

        row += 1
        # Low threshold
        ttk.Label(params_frame, text="Low Threshold:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(
            params_frame,
            from_=1,
            to=255,
            textvariable=self.low_threshold,
            width=10,
        ).grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="Lower threshold for edge detection").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )

        row += 1
        # High threshold
        ttk.Label(params_frame, text="High Threshold:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(
            params_frame,
            from_=1,
            to=255,
            textvariable=self.high_threshold,
            width=10,
        ).grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="Upper threshold for edge detection").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )

        row += 1
        # Line threshold
        ttk.Label(params_frame, text="Line Threshold:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(
            params_frame,
            from_=1,
            to=500,
            textvariable=self.line_threshold,
            width=10,
        ).grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="Accumulator threshold for line detection").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )

        row += 1
        # Min line length
        ttk.Label(params_frame, text="Min Line Length:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Spinbox(
            params_frame,
            from_=1,
            to=1000,
            textvariable=self.min_line_length,
            width=10,
        ).grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="Minimum line length to detect").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )

        row += 1
        # Max line gap
        ttk.Label(params_frame, text="Max Line Gap:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(
            params_frame,
            from_=1,
            to=100,
            textvariable=self.max_line_gap,
            width=10,
        ).grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="Maximum gap between line segments").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )

        # Progress and status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode="indeterminate")
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        # Status text
        self.status_text = tk.Text(status_frame, height=8, width=70, state="disabled", wrap=tk.WORD)
        self.status_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.status_text["yscrollcommand"] = scrollbar.set

        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)

        self.convert_button = ttk.Button(
            button_frame, text="Convert", command=self.start_conversion, width=15
        )
        self.convert_button.grid(row=0, column=0, padx=5)

        ttk.Button(button_frame, text="Clear", command=self.clear_fields, width=15).grid(
            row=0, column=1, padx=5
        )

        ttk.Button(button_frame, text="Exit", command=self.root.quit, width=15).grid(
            row=0, column=2, padx=5
        )

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

    def browse_input(self):
        """Browse for input image file."""
        filename = filedialog.askopenfilename(
            title="Select Input Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.tif *.tiff *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if filename:
            self.input_path.set(filename)
            # Auto-suggest output path
            if not self.output_path.get():
                base = os.path.splitext(filename)[0]
                self.output_path.set(base + ".dxf")

    def browse_output(self):
        """Browse for output DXF file."""
        filename = filedialog.asksaveasfilename(
            title="Save DXF File As",
            defaultextension=".dxf",
            filetypes=[("DXF files", "*.dxf"), ("All files", "*.*")],
        )
        if filename:
            self.output_path.set(filename)

    def browse_geojson(self):
        """Browse for output GeoJSON file."""
        filename = filedialog.asksaveasfilename(
            title="Save GeoJSON File As",
            defaultextension=".geojson",
            filetypes=[("GeoJSON files", "*.geojson"), ("All files", "*.*")],
        )
        if filename:
            self.geojson_path.set(filename)

    def log_message(self, message):
        """Add a message to the status text area."""
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")

    def clear_status(self):
        """Clear the status text area."""
        self.status_text.config(state="normal")
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state="disabled")

    def clear_fields(self):
        """Clear all input fields."""
        self.input_path.set("")
        self.output_path.set("")
        self.geojson_path.set("")
        self.clear_status()

    def validate_inputs(self):
        """Validate user inputs."""
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input image file.")
            return False

        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("Error", "Input image file does not exist.")
            return False

        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify an output DXF file.")
            return False

        if self.enable_geojson.get() and not self.geojson_path.get():
            messagebox.showerror(
                "Error", "Please specify a GeoJSON output file or disable GeoJSON export."
            )
            return False

        return True

    def start_conversion(self):
        """Start the conversion process in a separate thread."""
        if not self.validate_inputs():
            return

        # Disable convert button
        self.convert_button.config(state="disabled")
        self.clear_status()
        self.progress.start()

        # Run conversion in a separate thread to keep GUI responsive
        thread = threading.Thread(target=self.run_conversion, daemon=True)
        thread.start()

    def run_conversion(self):
        """Run the actual conversion process."""
        try:
            self.log_message("Starting conversion...")
            self.log_message(f"Input: {self.input_path.get()}")
            self.log_message(f"Output DXF: {self.output_path.get()}")

            geojson_output = self.geojson_path.get() if self.enable_geojson.get() else None
            if geojson_output:
                self.log_message(f"Output GeoJSON: {geojson_output}")

            self.log_message("\nParameters:")
            self.log_message(f"  Snap angle: {self.snap_angle.get()}°")
            self.log_message(
                f"  Edge detection: {self.low_threshold.get()}-{self.high_threshold.get()}"
            )
            self.log_message(f"  Line threshold: {self.line_threshold.get()}")
            self.log_message(f"  Min line length: {self.min_line_length.get()}")
            self.log_message(f"  Max line gap: {self.max_line_gap.get()}")

            self.log_message("\nProcessing...")

            result = convert_orthophoto_to_dxf(
                image_path=self.input_path.get(),
                dxf_output_path=self.output_path.get(),
                geojson_output_path=geojson_output,
                snap_angle=self.snap_angle.get(),
                low_threshold=self.low_threshold.get(),
                high_threshold=self.high_threshold.get(),
                line_threshold=self.line_threshold.get(),
                min_line_length=self.min_line_length.get(),
                max_line_gap=self.max_line_gap.get(),
            )

            self.log_message("\n✓ Conversion complete!")
            self.log_message(f"  Detected {result['lines_detected']} lines")
            self.log_message(f"  Snapped to {result['lines_snapped']} lines")
            self.log_message(f"  DXF saved to: {result['dxf_path']}")
            if result["geojson_path"]:
                self.log_message(f"  GeoJSON saved to: {result['geojson_path']}")

            # Show success message
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success",
                    f"Conversion completed successfully!\n\n"
                    f"Lines detected: {result['lines_detected']}\n"
                    f"Lines snapped: {result['lines_snapped']}",
                ),
            )

        except Exception as err:
            error_msg = str(err)
            self.log_message(f"\n✗ Error: {error_msg}")
            self.root.after(
                0, lambda msg=error_msg: messagebox.showerror("Error", f"Conversion failed:\n{msg}")
            )

        finally:
            # Re-enable button and stop progress
            self.root.after(0, lambda: self.convert_button.config(state="normal"))
            self.root.after(0, self.progress.stop)


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    OrthoPhotoConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
