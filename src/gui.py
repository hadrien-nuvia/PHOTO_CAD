"""GUI application for orthophoto to DXF conversion using tkinter."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import sys
import traceback
import queue
import atexit

# Support both relative imports (when used as module) and absolute imports (when run directly)
try:
    from .convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf
    from .learning import LearningSystem
except ImportError:
    try:
        from convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf
        from learning import LearningSystem
    except ImportError:
        from src.convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf
        from src.learning import LearningSystem


class OrthoPhotoConverterGUI:
    """GUI application for converting orthophotos to DXF."""

    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Orthophoto to DXF Converter")
        self.root.geometry("700x650")
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
        self.use_learned = tk.BooleanVar(value=False)

        # Learning system
        self.learning_system = LearningSystem()
        
        # Last conversion result
        self.last_result = None
        self.last_parameters = None

        # Thread management
        self.worker_thread = None
        self.is_running = False
        self.message_queue = queue.Queue()
        self._cleanup_done = False

        # Set up proper cleanup handlers
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        atexit.register(self.cleanup)

        self.create_widgets()

        # Start message queue processing
        self.process_queue()
        
        # Load learned parameters on startup if available
        self.load_learned_parameters()

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

        # Use learned parameters checkbox
        row = 0
        learned_frame = ttk.Frame(params_frame)
        learned_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Checkbutton(
            learned_frame, 
            text="Use learned parameters from feedback",
            variable=self.use_learned,
            command=self.on_use_learned_changed
        ).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(
            learned_frame,
            text="View Stats",
            command=self.show_statistics,
            width=12
        ).grid(row=0, column=1, padx=10)

        row += 1
        ttk.Separator(params_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5
        )
        
        row += 1
        # Snap angle
        ttk.Label(params_frame, text="Snap Angle (degrees):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.snap_angle_spinbox = ttk.Spinbox(
            params_frame,
            from_=1,
            to=90,
            textvariable=self.snap_angle,
            width=10,
        )
        self.snap_angle_spinbox.grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="Angle increment for snapping").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )

        row += 1
        # Low threshold
        ttk.Label(params_frame, text="Low Threshold:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.low_threshold_spinbox = ttk.Spinbox(
            params_frame,
            from_=1,
            to=255,
            textvariable=self.low_threshold,
            width=10,
        )
        self.low_threshold_spinbox.grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="Lower threshold for edge detection").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )

        row += 1
        # High threshold
        ttk.Label(params_frame, text="High Threshold:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.high_threshold_spinbox = ttk.Spinbox(
            params_frame,
            from_=1,
            to=255,
            textvariable=self.high_threshold,
            width=10,
        )
        self.high_threshold_spinbox.grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="Upper threshold for edge detection").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )

        row += 1
        # Line threshold
        ttk.Label(params_frame, text="Line Threshold:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.line_threshold_spinbox = ttk.Spinbox(
            params_frame,
            from_=1,
            to=500,
            textvariable=self.line_threshold,
            width=10,
        )
        self.line_threshold_spinbox.grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="Accumulator threshold for line detection").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )

        row += 1
        # Min line length
        ttk.Label(params_frame, text="Min Line Length:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.min_line_length_spinbox = ttk.Spinbox(
            params_frame,
            from_=1,
            to=1000,
            textvariable=self.min_line_length,
            width=10,
        )
        self.min_line_length_spinbox.grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="Minimum line length to detect").grid(
            row=row, column=2, sticky=tk.W, padx=5
        )

        row += 1
        # Max line gap
        ttk.Label(params_frame, text="Max Line Gap:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.max_line_gap_spinbox = ttk.Spinbox(
            params_frame,
            from_=1,
            to=100,
            textvariable=self.max_line_gap,
            width=10,
        )
        self.max_line_gap_spinbox.grid(row=row, column=1, sticky=tk.W, padx=5)
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
        
        self.feedback_button = ttk.Button(
            button_frame, text="Provide Feedback", command=self.show_feedback_dialog, width=15, state="disabled"
        )
        self.feedback_button.grid(row=0, column=1, padx=5)

        ttk.Button(button_frame, text="Clear", command=self.clear_fields, width=15).grid(
            row=0, column=2, padx=5
        )

        ttk.Button(button_frame, text="Exit", command=self.on_closing, width=15).grid(
            row=0, column=3, padx=5
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
    
    def load_learned_parameters(self):
        """Load learned parameters from feedback history."""
        if self.use_learned.get():
            try:
                params = self.learning_system.get_suggested_parameters(
                    image_path=self.input_path.get() if self.input_path.get() else None
                )
                self.snap_angle.set(params.get('snap_angle', 15))
                self.low_threshold.set(params.get('low_threshold', 50))
                self.high_threshold.set(params.get('high_threshold', 150))
                self.line_threshold.set(params.get('line_threshold', 100))
                self.min_line_length.set(params.get('min_line_length', 100))
                self.max_line_gap.set(params.get('max_line_gap', 10))
            except Exception as e:
                self.log_message(f"Could not load learned parameters: {e}")
    
    def on_use_learned_changed(self):
        """Handle changes to use learned parameters checkbox."""
        enabled = not self.use_learned.get()
        
        # Enable/disable parameter spinboxes
        state = "normal" if enabled else "readonly"
        self.snap_angle_spinbox.config(state=state)
        self.low_threshold_spinbox.config(state=state)
        self.high_threshold_spinbox.config(state=state)
        self.line_threshold_spinbox.config(state=state)
        self.min_line_length_spinbox.config(state=state)
        self.max_line_gap_spinbox.config(state=state)
        
        # Load learned parameters if checkbox is enabled
        if self.use_learned.get():
            self.load_learned_parameters()
    
    def show_statistics(self):
        """Show feedback statistics in a dialog."""
        stats = self.learning_system.get_statistics()
        
        if stats['total_feedback'] == 0:
            messagebox.showinfo("Feedback Statistics", "No feedback recorded yet.\n\nProvide feedback after conversions to help improve results!")
            return
        
        # Create statistics message
        msg = f"Total Feedback Entries: {stats['total_feedback']}\n"
        msg += f"Average Rating: {stats['average_rating']:.2f}/5.0\n\n"
        msg += "Rating Distribution:\n"
        for rating in range(5, 0, -1):
            count = stats['rating_distribution'].get(rating, 0)
            stars = '★' * rating
            msg += f"  {stars}: {count}\n"
        
        messagebox.showinfo("Feedback Statistics", msg)
    
    def show_feedback_dialog(self):
        """Show dialog to collect user feedback on last conversion."""
        if not self.last_result or not self.last_parameters:
            messagebox.showerror("Error", "No conversion result to provide feedback on.")
            return
        
        # Create feedback dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Provide Feedback")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Make it modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Rating
        ttk.Label(dialog, text="How satisfied are you with the result?", font=('', 10, 'bold')).pack(pady=10)
        
        rating_var = tk.IntVar(value=3)
        rating_frame = ttk.Frame(dialog)
        rating_frame.pack(pady=5)
        
        for i in range(1, 6):
            ttk.Radiobutton(
                rating_frame,
                text=f"{'★' * i} ({i}/5)",
                variable=rating_var,
                value=i
            ).pack(anchor=tk.W, padx=20)
        
        # Notes
        ttk.Label(dialog, text="Additional notes (optional):", font=('', 10)).pack(pady=(15, 5))
        notes_text = tk.Text(dialog, height=5, width=45, wrap=tk.WORD)
        notes_text.pack(padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        def submit_feedback():
            try:
                notes = notes_text.get("1.0", tk.END).strip()
                self.learning_system.add_feedback(
                    image_path=self.last_parameters['image_path'],
                    parameters={
                        'snap_angle': self.last_parameters['snap_angle'],
                        'low_threshold': self.last_parameters['low_threshold'],
                        'high_threshold': self.last_parameters['high_threshold'],
                        'line_threshold': self.last_parameters['line_threshold'],
                        'min_line_length': self.last_parameters['min_line_length'],
                        'max_line_gap': self.last_parameters['max_line_gap']
                    },
                    rating=rating_var.get(),
                    user_notes=notes if notes else None
                )
                
                messagebox.showinfo("Success", "Thank you for your feedback!\n\nYour feedback will help improve future conversions.")
                dialog.destroy()
                
                # Disable feedback button after submitting
                self.feedback_button.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save feedback: {e}")
        
        ttk.Button(button_frame, text="Submit", command=submit_feedback, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=5)

    def log_message(self, message):
        """Add a message to the status text area."""

        def _log():
            self.status_text.config(state="normal")
            self.status_text.insert(tk.END, message + "\n")
            self.status_text.see(tk.END)
            self.status_text.config(state="disabled")

        # Queue the log message for thread-safe execution
        self.message_queue.put(("log", _log))

    def clear_status(self):
        """Clear the status text area."""

        def _clear():
            self.status_text.config(state="normal")
            self.status_text.delete(1.0, tk.END)
            self.status_text.config(state="disabled")

        # Queue the clear operation for thread-safe execution
        self.message_queue.put(("clear", _clear))

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

        # Don't start if already running
        if self.is_running:
            messagebox.showwarning("Warning", "A conversion is already in progress.")
            return

        # Disable convert button
        self.convert_button.config(state="disabled")
        self.clear_status()
        self.progress.start()
        self.is_running = True

        # Run conversion in a separate thread (not daemon for proper cleanup)
        self.worker_thread = threading.Thread(target=self.run_conversion_safe, daemon=False)
        self.worker_thread.start()

    def run_conversion_safe(self):
        """Wrapper for run_conversion with proper exception handling."""
        try:
            self.run_conversion()
        except Exception as e:
            # Catch any unhandled exceptions
            error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
            self.log_message(f"\n✗ Error: {error_msg}")
            self.message_queue.put(
                (
                    "error",
                    lambda msg=str(e): messagebox.showerror("Error", f"Conversion failed:\n{msg}"),
                )
            )
        finally:
            # Always clean up
            self.is_running = False
            self.message_queue.put(("cleanup", lambda: self.convert_button.config(state="normal")))
            self.message_queue.put(("stop_progress", self.progress.stop))

    def run_conversion(self):
        """Run the actual conversion process."""
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
        
        # Store result and parameters for feedback
        self.last_result = result
        self.last_parameters = {
            'image_path': self.input_path.get(),
            'snap_angle': self.snap_angle.get(),
            'low_threshold': self.low_threshold.get(),
            'high_threshold': self.high_threshold.get(),
            'line_threshold': self.line_threshold.get(),
            'min_line_length': self.min_line_length.get(),
            'max_line_gap': self.max_line_gap.get()
        }

        self.log_message("\n✓ Conversion complete!")
        self.log_message(f"  Detected {result['lines_detected']} lines")
        self.log_message(f"  Snapped to {result['lines_snapped']} lines")
        self.log_message(f"  DXF saved to: {result['dxf_path']}")
        if result["geojson_path"]:
            self.log_message(f"  GeoJSON saved to: {result['geojson_path']}")
        
        self.log_message("\nYou can now provide feedback on this result!")

        # Enable feedback button
        self.message_queue.put(("enable_feedback", lambda: self.feedback_button.config(state="normal")))

        # Show success message
        self.message_queue.put(
            (
                "success",
                lambda res=result: messagebox.showinfo(
                    "Success",
                    f"Conversion completed successfully!\n\n"
                    f"Lines detected: {res['lines_detected']}\n"
                    f"Lines snapped: {res['lines_snapped']}\n\n"
                    f"You can now provide feedback to help improve future conversions.",
                ),
            )
        )

    def process_queue(self):
        """Process messages from the worker thread in a thread-safe manner."""
        try:
            while True:
                try:
                    msg_type, callback = self.message_queue.get_nowait()
                    callback()
                except queue.Empty:
                    break
                except Exception as e:
                    # Log individual callback errors but continue processing
                    print(f"Error in queue callback: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error processing queue: {e}", file=sys.stderr)
        finally:
            # Schedule next check - only if window still exists and we're not shutting down
            try:
                if self.root and self.root.winfo_exists():
                    self.root.after(100, self.process_queue)
            except tk.TclError:
                # Window is being destroyed, stop scheduling
                pass

    def on_closing(self):
        """Handle window close event."""
        if self.is_running:
            if messagebox.askokcancel(
                "Quit", "A conversion is in progress. Are you sure you want to quit?"
            ):
                self.cleanup()
                # Use destroy instead of quit for cleaner shutdown
                try:
                    self.root.destroy()
                except tk.TclError:
                    # Window already destroyed
                    pass
        else:
            self.cleanup()
            try:
                self.root.destroy()
            except tk.TclError:
                # Window already destroyed
                pass

    def cleanup(self):
        """Clean up resources before exit."""
        # Prevent multiple cleanup calls
        if hasattr(self, '_cleanup_done') and self._cleanup_done:
            return

        self._cleanup_done = True
        self.is_running = False

        # Wait for worker thread to finish (with timeout)
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)


def main():
    """Main entry point for the GUI application."""
    root = None
    try:
        root = tk.Tk()
        OrthoPhotoConverterGUI(root)  # noqa: F841 - GUI instance attached to root
        root.mainloop()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nInterrupted by user", file=sys.stderr)
        if root:
            try:
                root.destroy()
            except tk.TclError:
                pass
        sys.exit(0)
    except Exception as e:
        # Catch any uncaught exceptions at top level
        print(f"Fatal error: {e}", file=sys.stderr)
        traceback.print_exc()
        try:
            messagebox.showerror("Fatal Error", f"Application error:\n{str(e)}")
        except Exception:
            # If messagebox fails (e.g., no display), just print
            pass
        sys.exit(1)
    finally:
        # Ensure cleanup happens
        if root:
            try:
                root.quit()
            except tk.TclError:
                pass


if __name__ == "__main__":
    main()
