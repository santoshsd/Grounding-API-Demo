import { ImageResponse } from "next/og";

export const size = { width: 32, height: 32 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          background: "#0b0d10",
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: 7,
        }}
      >
        {/* outer ring */}
        <div
          style={{
            width: 20,
            height: 20,
            borderRadius: "50%",
            border: "3px solid #7aa2f7",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {/* center dot */}
          <div
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: "#9ece6a",
            }}
          />
        </div>
      </div>
    ),
    { ...size },
  );
}
